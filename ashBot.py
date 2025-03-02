import discord
import openai
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

# Create bot with application command support
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree  # Create the command tree for slash commands

@bot.event
async def on_ready():
    await tree.sync()  # Sync slash commands with Discord
    print(f'✅ Logged in as {bot.user}, Slash Commands Synced!')

async def load_cogs():
    """Load all cogs (command files)"""
    await bot.load_extension("cogs.chat")

async def main():
    """Main function to start bot"""
    async with bot:
        await load_cogs()  # Load cogs before starting bot
        await bot.start(DISCORD_BOT_TOKEN)  # Properly start the bot

# Run the bot correctly
asyncio.run(main())
