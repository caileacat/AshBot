import discord
from discord.ext import commands
import os
from .subprocesses.admin_actions import handle_admin_action
from .subprocesses.process_recent_messages import process_recent_messages
from .subprocesses.send_to_openai import send_to_openai
from .subprocesses.process_response import process_response
from .subprocesses.weaviate_memory import save_user_memory, load_user_memory, setup_weaviate

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
        """Handles interaction with Ash."""
        await interaction.response.defer(thinking=True)
        username = interaction.user.name

        # Fetch debug channel
        debug_channel = await self.fetch_debug_channel()
        if debug_channel:
            await debug_channel.send(f"🚀 **DEBUG:** Ash command received from `{username}`: `{query}`")

        # ✅ Load user memory from Weaviate
        user_memory = await load_user_memory(str(interaction.user.id), debug_channel)

        # ✅ Ensure user exists in memory
        if "info" not in user_memory:
            user_memory["info"] = {"name": username, "role": "New Acquaintance"}
            await save_user_memory(str(interaction.user.id), user_memory, debug_channel)

        # ✅ Get last messages from the channel
        recent_chat = await process_recent_messages(interaction, debug_channel)

        # ✅ Get OpenAI response
        ash_reply = await send_to_openai(username, query, user_memory, recent_chat, debug_channel)

        # ✅ Process and clean response
        final_response = await process_response(interaction, username, query, ash_reply, debug_channel)

        # ✅ Store new information in Weaviate if Ash provides it
        if "NEW INFO:" in ash_reply:
            new_info = {}
            for line in ash_reply.split("\n"):
                if line.startswith("NEW INFO:"):
                    try:
                        key, value = line.replace("NEW INFO:", "").strip().split(": ", 1)
                        new_info[key.strip()] = value.strip()
                    except ValueError:
                        pass
            
            # ✅ Merge new info into memory
            if new_info:
                user_memory.update(new_info)
                await save_user_memory(str(interaction.user.id), user_memory, debug_channel)

        await interaction.followup.send(final_response)

async def setup(bot):
    await bot.add_cog(Chat(bot))
