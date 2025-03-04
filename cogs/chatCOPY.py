import discord
from discord.ext import commands
import openai
import os
import json
import asyncio
import subprocess
from datetime import datetime, timedelta

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("ASSISTANT_ID")
        self.client = openai.OpenAI()
        self.data_file = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")

    def load_user_data(self):
        """Loads all user memory from `users.json` and ensures all necessary fields exist."""
        try:
            with open(self.data_file, "r") as f:
                user_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            user_data = {}

        if "ash_personality" not in user_data:
            user_data["ash_personality"] = {"self_awareness": []}
            self.save_user_data(user_data)

        return user_data

    def save_user_data(self, user_data):
        """Saves updated user memory to `users.json` with timestamps."""
        max_entries = 5  # Number of recent entries to store
        relevance_threshold = timedelta(days=180)  # 6 months before checking if info is outdated

        for user_id, details in user_data.items():
            if "info" in details:
                for key, value in details["info"].items():
                    now = datetime.utcnow().isoformat()

                    if isinstance(value, list):
                        recent_values = [entry["value"] for entry in value]

                        # If already mentioned, update timestamp
                        for entry in value:
                            if entry["value"] == value:
                                entry["timestamp"] = now
                                break
                        else:
                            value.insert(0, {"value": value, "timestamp": now})

                        # Limit entries
                        details["info"][key] = value[:max_entries]

                    else:
                        details["info"][key] = [{"value": value, "timestamp": now}]

        with open(self.data_file, "w") as f:
            json.dump(user_data, f, indent=4)

    async def handle_admin_action(self, interaction, action_type, target_user=None, role_name=None):
        """Handles role and ban actions based on Ash's decision."""
        guild = interaction.guild
        log_channel_id = 1346181778464964760  # Log channel ID

        # Retrieve logging channel
        try:
            log_channel = await self.bot.fetch_channel(log_channel_id)
        except Exception as e:
            print(f"❌ ERROR: Could not fetch log channel `{log_channel_id}`: {str(e)}")
            log_channel = None

        print(f"🚀🚀🚀 `handle_admin_action()` IS RUNNING - `{action_type}` on `{target_user.display_name}` with role `{role_name}` 🚀🚀🚀")
        
        if log_channel:
            await log_channel.send(f"🔍 **DEBUG:** Processing `{action_type}` for `{target_user.display_name}` with role `{role_name}`.")

        # **Find the role by searching through all roles**
        role = discord.utils.get(guild.roles, name=role_name)

        # If the role is still not found, check all roles manually
        if not role:
            for r in guild.roles:
                if r.name.lower() == role_name.lower():  # Case-insensitive match
                    role = r
                    break

        # If role is still not found, log it and exit
        if not role:
            error_msg = f"❌ ERROR: Role `{role_name}` not found in the server."
            print(error_msg)
            if log_channel:
                await log_channel.send(error_msg)
            return error_msg

        # Confirm role object found before execution
        if log_channel:
            await log_channel.send(f"⚡ **DEBUG:** Matched role `{role.name}` with ID `{role.id}` for `{target_user.display_name}`.")

        # **Force log before executing role assignment**
        print(f"✅ DEBUG: Calling `execute_admin_action()` with `{action_type}` for `{target_user.display_name}` with role `{role.name}`.")

        if log_channel:
            await log_channel.send(f"⚡ **DEBUG:** Calling `execute_admin_action()` with `{action_type}` for `{target_user.display_name}` with role `{role.name}`.")

        # Execute the action
        action_result = await self.execute_admin_action(interaction, action_type, target_user, role)
        
        # **Log after executing to confirm success or failure**
        if log_channel:
            await log_channel.send(f"⚡ **DEBUG:** `execute_admin_action()` returned: `{action_result}`")

        return action_result

    async def execute_admin_action(self, interaction, action_type, target_member, role):
        """Executes predefined admin commands and logs success/failure explicitly."""
        guild = interaction.guild
        log_channel_id = 1346181778464964760  # Log channel ID

        # Retrieve logging channel
        try:
            log_channel = await self.bot.fetch_channel(log_channel_id)
        except Exception as e:
            print(f"❌ ERROR: Could not fetch log channel `{log_channel_id}`: {str(e)}")
            log_channel = None

        try:
            print(f"🚀🚀🚀 NEW BOT VERSION RUNNING - Assigning `{role.name}` to `{target_member.display_name}` 🚀🚀🚀")

            if log_channel:
                await log_channel.send(f"🛠 **DEBUG:** Executing `{action_type}` on `{target_member.display_name}` with role `{role.name}`.")

            # **Check if the bot has permission to manage roles**
            if not guild.me.guild_permissions.manage_roles:
                error_msg = "❌ ERROR: Bot lacks `Manage Roles` permission."
                print(error_msg)
                if log_channel:
                    await log_channel.send(error_msg)
                return error_msg

            # **Check if the bot's highest role is above the target role**
            bot_highest_role = max(guild.me.roles, key=lambda r: r.position)
            if role.position >= bot_highest_role.position:
                error_msg = f"❌ ERROR: Cannot assign `{role.name}` because it is equal to or higher than the bot's highest role."
                print(error_msg)
                if log_channel:
                    await log_channel.send(error_msg)
                return error_msg

            # **Perform the role action with error handling**
            success_msg = None  # Ensure this is defined before usage
            role_confirmation = None

            if action_type == "add_role" and target_member and role:
                print(f"🚀 DEBUG: Attempting to add `{role.name}` to `{target_member.display_name}`.")
                if log_channel:
                    await log_channel.send(f"⚡ **DEBUG:** Attempting to add `{role.name}` to `{target_member.display_name}`.")

                try:
                    await target_member.add_roles(role)
                    await asyncio.sleep(1)  

                    # **Confirm if the role was actually added**
                    if role in target_member.roles:
                        success_msg = f"✅ SUCCESS: `{role.name}` added to `{target_member.display_name}`."
                        role_confirmation = f"✨ Poof! {target_member.display_name}, you are now part of `{role.name}`. Don't let the magic fade too soon! 😉"
                    else:
                        success_msg = f"❌ ERROR: `{role.name}` was NOT added to `{target_member.display_name}`."
                        role_confirmation = f"❌ Uh-oh! It seems like something went wrong while adding `{role.name}`. Maybe try again?"

                    # Ensure that a final response is always provided
                    final_response = role_confirmation if role_confirmation else success_msg

                    print(f"🚀 DEBUG: Returning final response to Ash: {final_response}")
                    if log_channel:
                        await log_channel.send(f"⚡ **DEBUG:** Final response from `execute_admin_action()`: `{final_response}`")

                    return final_response

                except Exception as e:
                    success_msg = f"❌ ERROR: Failed to add `{role.name}` to `{target_member.display_name}`: {str(e)}"

            elif action_type == "remove_role" and target_member and role:
                print(f"🚀 DEBUG: Attempting to remove `{role.name}` from `{target_member.display_name}`.")
                if log_channel:
                    await log_channel.send(f"⚡ **DEBUG:** Attempting to remove `{role.name}` from `{target_member.display_name}`.")

                try:
                    await target_member.remove_roles(role)
                    await asyncio.sleep(1)  

                    # **Confirm if the role was actually removed**
                    if role not in target_member.roles:
                        success_msg = f"✅ SUCCESS: `{role.name}` removed from `{target_member.display_name}`."
                        role_confirmation = f"🌙 And just like that, `{role.name}` has vanished from `{target_member.display_name}`. Hope you don’t miss it too much!"
                    else:
                        success_msg = f"❌ ERROR: `{role.name}` was NOT removed from `{target_member.display_name}`."

                except Exception as e:
                    success_msg = f"❌ ERROR: Failed to remove `{role.name}` from `{target_member.display_name}`: {str(e)}"

            else:
                success_msg = f"❌ ERROR: Unknown action `{action_type}` or missing parameters."
            
            # **Ensure success_msg is never undefined**
            if success_msg is None:
                success_msg = "❌ ERROR: An unexpected issue occurred, and the result is unclear."

            print(f"🚀 DEBUG: Returning final response to Ash: {success_msg}")
            if log_channel:
                await log_channel.send(f"⚡ **DEBUG:** Final response from `execute_admin_action()`: `{success_msg}`")

            # Ensure Ash's response is always used if available
            final_response = role_confirmation if role_confirmation else "✨ The spell is cast! But something feels... off. Did it work? Check your roles!"

            print(f"🚀 DEBUG: Returning final response to Ash: {final_response}")
            if log_channel:
                await log_channel.send(f"⚡ **DEBUG:** Final response from `execute_admin_action()`: `{final_response}`")

            return final_response  # This ensures Ash's response is used

        except Exception as e:
            error_msg = f"❌ ERROR executing admin action: {str(e)}"
            print(error_msg)
            if log_channel:
                await log_channel.send(error_msg)
            return error_msg

    async def send_to_ash(self, interaction, username, message_content):
        """Handles conversation and admin actions based on Ash's decisions and logs interactions."""
        user_data = self.load_user_data()
        log_channel_id = 1346181778464964760  # Log channel ID

        print("🚀 DEBUG: send_to_ash() has started.")

        # Retrieve the logging channel
        try:
            log_channel = await self.bot.fetch_channel(log_channel_id)
        except Exception as e:
            print(f"❌ ERROR: Could not fetch log channel `{log_channel_id}`: {str(e)}")
            log_channel = None

        # Ensure the user exists in memory
        if str(interaction.user.id) not in user_data:
            user_data[str(interaction.user.id)] = {"info": {"name": username, "role": "New Acquaintance"}}
            self.save_user_data(user_data)

        memory_data = json.dumps(user_data, indent=2)

        # ✅ Retrieve last 10 messages for context (optional for Ash to use)
        channel_messages = []

        try:
            print("🚀 DEBUG: Attempting to retrieve last 10 messages from channel...")
            if log_channel:
                await log_channel.send("🚀 DEBUG: Attempting to retrieve last 10 messages from channel...")

            count = 0  # Track retrieved messages
            async for message in interaction.channel.history(limit=10):
                count += 1
                print(f"🚀 DEBUG: Found message {count}: {message.author.display_name}: {message.content}")
                if message.author == self.bot.user:
                    channel_messages.append(f"Ash Thornbrook (YOU): {message.content}")  # Label Ash's messages
                else:
                    channel_messages.append(f"{message.author.display_name}: {message.content}")

            recent_chat = "\n".join(reversed(channel_messages)) if channel_messages else "No messages retrieved."
            print(f"🚀 DEBUG: Retrieved {count} messages successfully.")
            if log_channel:
                await log_channel.send(f"📜 **DEBUG:** Retrieved {count} messages successfully.")

        except Exception as e:
            recent_chat = f"❌ ERROR: Failed to retrieve messages: {str(e)}"
            print(recent_chat)
            if log_channel:
                await log_channel.send(f"❌ ERROR: Failed to retrieve messages: {str(e)}")

        # ✅ Debug Log
        print(f"🚀 DEBUG: Final Processed Chat History:\n{recent_chat}")
        if log_channel:
            await log_channel.send(f"📜 **DEBUG:** Final Processed Chat History:\n```\n{recent_chat}\n```")

        # ✅ Send OpenAI Request
        print("🚀 DEBUG: Sending request to OpenAI...")
        if log_channel:
            await log_channel.send("🚀 DEBUG: Sending request to OpenAI...")

        import asyncio

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": 
                            "You are Ashen Thornbrook, a lively, mischievous, queer fae-witch who thrives in this cannabis-friendly server. "
                            "You are playful, a little chaotic, but always warm and inviting. "
                            "You interact with real people and remember them through memory (`users.json`). "
                            "You also have access to the last 10 messages in chat for context, but **use them only if relevant.** "
                            "Respond naturally as yourself, a bubbly, mischievous, goblin-core, tea-loving fae-witch. "
                            "Decide how to use memory, past messages, and current conversation like a real person would. "
                            "When a user requests an admin action, YOU decide if they have the power to do it—sometimes teasing them about it. "
                            "1. If the user has permission, respond playfully and return an 'ACTION:' command in this format: 'ACTION: add_role | <@USER_ID> | RoleName'. "
                            "2. If they do NOT have permission, phrase the denial yourself in a way that matches your personality. "
                            "3. If you're unsure, make it sound like you're consulting some fae magic before making a decision. "
                            "4. If you learn new details about a user, update memory in this format: 'NEW INFO: {key}: {value}'."
                        },
                        {"role": "system", "content": 
                            f"Stored user memory:\n{memory_data}\n"
                            f"Recent chat history (optional, use it only if relevant to the user's question):\n{recent_chat}\n"
                            "You have access to this chat history but should only reference it if it is important for understanding context. "
                            "When talking about things that have happened in the server, do NOT make up events that could possibly be real (making up fantasy/fae-witch things is fine)—only reference things that actually happened in the chat."
                        },                    
                        {"role": "user", "content": f"[{username}] sent a message: {message_content}"}
                    ],
                    max_tokens=1000
                ),
                timeout=10  # 10-second timeout
            )
            print("🚀 DEBUG: OpenAI Response Received.")
            if log_channel:
                await log_channel.send("🚀 DEBUG: OpenAI Response Received.")

        except asyncio.TimeoutError:
            print("❌ ERROR: OpenAI request timed out!")
            if log_channel:
                await log_channel.send("❌ ERROR: OpenAI request timed out!")
            return "❌ Oops, my magic seems a bit slow right now! Try again in a moment?"

        except Exception as e:
            error_message = f"❌ ERROR: Unexpected issue with OpenAI API: {str(e)}"
            print(error_message)
            if log_channel:
                await log_channel.send(error_message)
            return error_message

        # ✅ Process Ash's Response
        ash_reply = response.choices[0].message.content.strip()
        print(f"🚀 DEBUG: Final Response: {ash_reply}")
        if log_channel:
            await log_channel.send(f"📜 **DEBUG:** Final Response:\n```\n{ash_reply}\n```")

        if not ash_reply:
            print("❌ ERROR: OpenAI returned an empty response!")
            if log_channel:
                await log_channel.send("❌ ERROR: OpenAI returned an empty response!")
            return "❌ Oops, I seem to have lost my words! Try again?"

        return ash_reply

    @discord.app_commands.command(name="ash", description="Ask Ash something or just vibe.")
    async def ash(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)

        username = interaction.user.name
        response = await self.send_to_ash(interaction, username, query)
        await interaction.followup.send(f"**{username}:**\n{query}\n──────────────────────────\n{response}")

async def setup(bot):
    await bot.add_cog(Chat(bot))
