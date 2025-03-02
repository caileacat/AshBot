import discord
from discord.ext import commands
import openai
import os
import asyncio

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("ASSISTANT_ID")
        openai.api_key = self.api_key

    async def send_to_ash(self, message_content):
        """Send a message to Ash and return the response."""
        try:
            # Create a new thread for the conversation
            thread = openai.beta.threads.create()

            # Start a run with the assistant
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )

            # Wait for the assistant to process the request
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,  # ✅ Fixed: Added thread_id here
                    run_id=run.id
                )
                if run_status.status in ["completed", "failed"]:
                    break
                await asyncio.sleep(1)  # Avoid excessive API calls

            if run_status.status == "failed":
                return "❌ Ash encountered an error processing the request."

            # Retrieve messages from the thread
            messages = openai.beta.threads.messages.list(thread_id=thread.id)

            if messages.data:
                return messages.data[0].content[0].text.value  # Extract response text
            else:
                return "❌ No response from Ash."

        except Exception as e:
            return f"❌ Error: {str(e)}"

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Chat Cog Loaded!")

    @discord.app_commands.command(name="ash", description="Chat with Ash (ChatGPT Project)")
    async def ash(self, interaction: discord.Interaction, query: str):
        """Slash command to chat with Ash."""
        await interaction.response.defer()  # Show "thinking" status
        try:
            response = await self.send_to_ash(query)
            await interaction.followup.send(response)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Chat(bot))
