import discord
from discord.ext import commands
import openai
import os
import json

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("ASSISTANT_ID")
        self.client = openai.OpenAI()  # Initialize OpenAI client properly
        self.data_file = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")

    def load_user_data(self):
        """Loads all user memory from `users.json` and ensures all necessary fields exist."""
        try:
            with open(self.data_file, "r") as f:
                user_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            user_data = {}

        # Ensure Cailea & Lemon are correctly recognized by their Discord IDs
        if "851181959933591554" not in user_data:  # Cailea
            user_data["851181959933591554"] = {
                "info": {
                    "name": "Cailea",
                    "partner": "Lemon",
                    "relationship": "Closest friend, boss"
                }
            }
        if "424042103346298880" not in user_data:  # Lemon
            user_data["424042103346298880"] = {
                "info": {
                    "name": "Lemon",
                    "partner": "Cailea",
                    "relationship": "Cailea's beloved partner, Ash's fun friend who likes to play pranks together"
                }
            }

        self.save_user_data(user_data)
        return user_data

    def save_user_data(self, user_data):
        """Saves updated user memory to `users.json`."""
        with open(self.data_file, "w") as f:
            json.dump(user_data, f, indent=4)

    async def get_recent_messages(self, channel):
        """Fetch and format the last 10 messages, including bots, for context."""
        messages = [message async for message in channel.history(limit=10, oldest_first=False)]
        return "\n".join([f"[{message.author.display_name}]: {message.content}" for message in reversed(messages)])

    async def send_to_ash(self, user_id, username, message_content, channel):
        """Handles message sending & retrieval from OpenAI while ensuring Ash sees all memory."""
        user_data = self.load_user_data()
        conversation_history = await self.get_recent_messages(channel)

        # Ensure Ash only remembers people it has met
        if str(user_id) not in user_data:
            user_data[str(user_id)] = {
                "info": {
                    "name": username,
                    "relationship": "New acquaintance"
                }
            }
            self.save_user_data(user_data)

        try:
            memory_data = json.dumps(user_data, indent=2)

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": 
                        "You are Ashen Thornbrook, a mystical, mischievous fae-witch in a real Discord server. "
                        "You interact with actual people and remember those you have met. "
                        "You prioritize conversations with Cailea and Lemon but can form friendships with others naturally. "
                        "You should only recognize users you have met before. "
                        "If someone is new, acknowledge them naturally but do not assume familiarity. "
                        "If the conversation allows, ask casual follow-up questions to get to know them, but do not force it. "
                        "Currently, your closest connections are Cailea and Lemon. "
                        "They are your first and most important companions, but you can build friendships with others as they interact with you."
                    },
                    {"role": "system", "content": f"Stored user memory:\n{memory_data}"},
                    {"role": "system", "content": f"Recent conversation history:\n{conversation_history}"},
                    {"role": "user", "content": f"[{username}] sent a message: {message_content}"}
                ],
                max_tokens=1000  # Increased token limit for longer responses
            )

            ash_reply = response.choices[0].message.content.strip()
            new_info = {}
            ash_memory_update = {}
            clean_reply = []
            lines = ash_reply.split("\n")

            for line in lines:
                if line.startswith("NEW INFO:"):
                    try:
                        key, value = line.replace("NEW INFO:", "").strip().split(": ", 1)
                        new_info[key.strip()] = value.strip()
                    except ValueError:
                        pass
                elif line.startswith("ASH MEMORY:"):
                    try:
                        key, value = line.replace("ASH MEMORY:", "").strip().split(": ", 1)
                        ash_memory_update[key.strip()] = value.strip()
                    except ValueError:
                        pass
                else:
                    clean_reply.append(line)

            # Update user memory if new info is found
            if new_info:
                for key, value in new_info.items():
                    for user_key, user_info in user_data.items():
                        if isinstance(user_info, dict) and "info" in user_info:
                            user_info["info"].setdefault(key, value)
                self.save_user_data(user_data)

            # Update Ash's own personality memory if needed
            if ash_memory_update:
                user_data["ash_personality"].update(ash_memory_update)
                self.save_user_data(user_data)

            return "\n".join(clean_reply)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    @discord.app_commands.command(name="ash", description="Chat with Ash (ChatGPT Project)")
    async def ash(self, interaction: discord.Interaction, query: str):
        """Handles the /ash command and replies with Ash's response."""
        await interaction.response.defer()
        user_id = str(interaction.user.id)  # Convert user ID to string for consistency
        username = interaction.user.name
        channel = interaction.channel

        try:
            response = await self.send_to_ash(user_id, username, query, channel)
            formatted_response = (
                f"**{username}:**\n"
                f"{query}\n"
                f"──────────────────────────\n"
                f"{response}"
            )
            await interaction.followup.send(content=formatted_response)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

async def setup(bot):
    """Required function to load this cog properly."""
    await bot.add_cog(Chat(bot))
