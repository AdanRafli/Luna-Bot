import discord
from discord.ext import commands
import asyncio
import os

# Mengatur intents agar bot bisa membaca pesan, mengetahui server, dan anggota
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Wajib agar bot dapat membaca isi pesan
intents.guilds = True
intents.members = True         # Untuk fitur moderasi yang membutuhkan informasi member

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")

async def load_extensions():
    """Memuat semua file .py dalam folder 'commands/' sebagai extension."""
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            extension = f"commands.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                print(f"✅ Loaded: {extension}")
            except Exception as e:
                print(f"❌ Failed to load {extension}: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
