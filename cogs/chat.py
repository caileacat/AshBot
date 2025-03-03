import discord
from discord.ext import commands
import openai
import os
import asyncio
import json

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("ASSISTANT_ID")
        openai.api_key = self.api_key
        self.data_file = "data/users.json"

    def load_user_data(self):
        """Load user memory data from JSON."""
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_user_data(self, user_data):
        """Save updated user memory data to JSON."""
        with open(self.data_file, "w") as f:
            json.dump(user_data, f, indent=4)

    async def get_recent_messages(self, channel):
        """Fetch and format the last 20 messages, including bots."""
        messages = [message async for message in channel.history(limit=20, oldest_first=False)]
        conversation = []

        for message in reversed(messages):  # Reverse to keep chronological order
            conversation.append(f"[{message.author.display_name}]: {message.content}")

        return "\n".join(conversation)

    async def send_to_ash(self, user_id, username, message_content, channel):
        try:
            user_data = self.load_user_data()
            if str(user_id) not in user_data:
                user_data[str(user_id)] = {"username": username, "info": {}}

            # Fetch recent conversation in the channel
            conversation_history = await self.get_recent_messages(channel)

            # Format the final prompt
            prompt = (
                "Recent conversation:\n"
                f"{conversation_history}\n\n"
                f"Now, [{username}] is talking to you. Here’s their message:\n"
                f"[{username}]: {message_content}\n\n"
                "Reply to their message naturally. If you learn anything new about them, include it in the format:\n"
                "NEW INFO: {key}: {value}\n"
                "Otherwise, just respond normally."
            )

            # 🔹 New OpenAI API Call
            client = openai.OpenAI()  # Properly initialize OpenAI client
            response = client.chat.completions.create(
                model="gpt-4",  # Change to "gpt-3.5-turbo" if needed
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )

            ash_reply = response.choices[0].message.content.strip()

            # Extract new user info if Ash provides it
            new_info = {}
            lines = ash_reply.split("\n")
            final_response = []
            for line in lines:
                if line.startswith("NEW INFO:"):
                    try:
                        key, value = line.replace("NEW INFO:", "").strip().split(": ", 1)
                        new_info[key.strip()] = value.strip()
                    except ValueError:
                        pass  # Ignore bad formatting
                else:
                    final_response.append(line)

            final_response_text = "\n".join(final_response)

            # Update user data with new info
            if new_info:
                user_data[str(user_id)]["info"].update(new_info)
                self.save_user_data(user_data)

            return final_response_text

        except Exception as e:
            return f"❌ Error: {str(e)}"


    @discord.app_commands.command(name="ash", description="Chat with Ash (ChatGPT Project)")
    async def ash(self, interaction: discord.Interaction, query: str):
        """Handles the /ash command and replies with Ash's response."""
        await interaction.response.defer()
        user_id = interaction.user.id
        username = interaction.user.name
        channel = interaction.channel  # Get the channel where the command was used

        try:
            # Get the response from Ash with the conversation context
            response = await self.send_to_ash(user_id, username, query, channel)

            # Create the Embed with user tag
            embed = discord.Embed(
                title=f"Ash's Response to {interaction.user.mention}",
                color=discord.Color.blue()
            )
            embed.add_field(name="🗣 Your Message", value=query, inline=False)
            embed.add_field(name="🤖 Ash’s Reply", value=response, inline=False)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

    @discord.app_commands.command(name="clear_memory", description="Clears all stored user memory from Ash.")
    @commands.has_permissions(administrator=True)  # Optional: Restricts command to admins
    async def clear_memory(self, interaction: discord.Interaction):
        """Clears all user memory stored in users.json"""
        self.save_user_data({})  # Overwrite with an empty dictionary
        await interaction.response.send_message("🧹 Ash's memory has been cleared!", ephemeral=True)

async def setup(bot):
    """Required function to load this cog properly."""
    await bot.add_cog(Chat(bot))
