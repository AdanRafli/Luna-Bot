import discord
from discord.ext import commands
import yt_dlp
import asyncio
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("music")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("❌ You need to be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            try:
                self.voice_clients[ctx.guild.id] = await channel.connect()
                await ctx.send(f"✅ Joined {channel.name}!")
            except Exception as e:
                logger.error(f"Failed to join voice channel: {e}")
                await ctx.send("❌ Unable to join voice channel.")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is None:
            await ctx.send("❌ I'm not in a voice channel.")
            return
        await ctx.voice_client.disconnect()
        del self.voice_clients[ctx.guild.id]
        await ctx.send("✅ Left the voice channel.")

    @commands.command()
    async def play(self, ctx, *, search: str):
        if ctx.voice_client is None:
            await ctx.send("❌ I need to be in a voice channel first. Use !join.")
            return
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }

        await ctx.send(f"🔎 Searching for: {search}")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                logger.info(f"Search result: {info}")
                if 'entries' not in info or not info['entries']:
                    await ctx.send("❌ No results found.")
                    return
                url = info['entries'][0]['url']
                title = info['entries'][0]['title']
        except Exception as e:
            logger.error(f"Error during YouTube search: {e}")
            await ctx.send("❌ Failed to search for the song.")
            return

        try:
            source = await discord.FFmpegOpusAudio.from_probe(url, method='fallback')
            ctx.voice_client.play(source)
            await ctx.send(f"🎵 Now playing: {title}")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            await ctx.send("❌ Failed to play the song.")

async def setup(bot):
    await bot.add_cog(Music(bot))
