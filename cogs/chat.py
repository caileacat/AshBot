import discord
from discord.ext import commands
import os
from .subprocesses.admin_actions import handle_admin_action
from .subprocesses.memory import load_user_data, save_user_data
from .subprocesses.process_recent_messages import process_recent_messages
from .subprocesses.send_to_openai import send_to_openai
from .subprocesses.process_response import process_response

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("ASSISTANT_ID")
        self.debug_channel_id = 1346181778464964760  # Debug channel ID

    async def fetch_debug_channel(self):
        """Fetches the debug logging channel."""
        try:
            return await self.bot.fetch_channel(self.debug_channel_id)
        except Exception as e:
            print(f"❌ ERROR: Could not fetch debug channel `{self.debug_channel_id}`: {str(e)}")
            return None

    @discord.app_commands.command(name="ash", description="Ask Ash something or just vibe.")
    async def ash(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)
        username = interaction.user.name

        # Fetch debug channel
        debug_channel = await self.fetch_debug_channel()
        if debug_channel:
            await debug_channel.send(f"🚀 **DEBUG:** Ash command received from `{username}`: `{query}`")

        # Load memory
        user_data = load_user_data()

        # Ensure user exists in memory
        if str(interaction.user.id) not in user_data:
            user_data[str(interaction.user.id)] = {"info": {"name": username, "role": "New Acquaintance"}}
            save_user_data(user_data)

        # Get last messages from the channel
        recent_chat = await process_recent_messages(interaction, debug_channel)

        # Get OpenAI response
        ash_reply = await send_to_openai(username, query, user_data, recent_chat, debug_channel)

        # Process the final response
        final_response = await process_response(interaction, username, query, ash_reply, debug_channel)

        # await interaction.followup.send(final_response)

async def setup(bot):
    await bot.add_cog(Chat(bot))
