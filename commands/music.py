from discord.ext import commands
import discord
import yt_dlp
import asyncio

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  # Menyimpan voice client per guild
        self.queues = {}         # Menyimpan antrian lagu per guild

    async def ensure_voice(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.guild.id not in self.voice_clients or not self.voice_clients[ctx.guild.id].is_connected():
                vc = await channel.connect()
                self.voice_clients[ctx.guild.id] = vc
            return self.voice_clients[ctx.guild.id]
        else:
            await ctx.send("❌ You must be in a voice channel!")
            return None

    @commands.command(name="join")
    async def join(self, ctx):
        await self.ensure_voice(ctx)
        await ctx.send("🎵 Luna has joined the voice channel!")

    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.guild.id in self.voice_clients:
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
            self.queues.pop(ctx.guild.id, None)
            await ctx.send("👋 Luna has left the voice channel!")
        else:
            await ctx.send("❌ I'm not in a voice channel!")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        vc = await self.ensure_voice(ctx)
        if not vc:
            return

        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'extractaudio': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            if 'entries' not in info or not info['entries']:
                await ctx.send("❌ No results found.")
                return
            url = info['entries'][0]['url']
            title = info['entries'][0]['title']

        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []

        if vc.is_playing() or vc.is_paused():
            self.queues[ctx.guild.id].append((url, title))
            await ctx.send(f"➕ Added **{title}** to the queue!")
        else:
            self.queues[ctx.guild.id].append((url, title))
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
            next_url, title = self.queues[ctx.guild.id].pop(0)
            FFMPEG_OPTIONS = {'options': '-vn'}
            source = discord.FFmpegPCMAudio(next_url, **FFMPEG_OPTIONS)
            vc = self.voice_clients[ctx.guild.id]
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
            await ctx.send(f"🎶 Now playing: **{title}**")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.guild.id in self.voice_clients and self.voice_clients[ctx.guild.id].is_playing():
            self.voice_clients[ctx.guild.id].pause()
            await ctx.send("⏸️ Music paused.")
        else:
            await ctx.send("❌ No music is playing!")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.guild.id in self.voice_clients and self.voice_clients[ctx.guild.id].is_paused():
            self.voice_clients[ctx.guild.id].resume()
            await ctx.send("▶️ Music resumed.")
        else:
            await ctx.send("❌ No music is paused!")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.guild.id in self.voice_clients and self.voice_clients[ctx.guild.id].is_playing():
            self.voice_clients[ctx.guild.id].stop()
            self.queues[ctx.guild.id] = []
            await ctx.send("⏹️ Music stopped.")
        else:
            await ctx.send("❌ No music is playing!")

    @commands.command(name="skip")
    async def skip(self, ctx):
        if ctx.guild.id in self.voice_clients and self.voice_clients[ctx.guild.id].is_playing():
            self.voice_clients[ctx.guild.id].stop()
            await ctx.send("⏭️ Skipped the current track.")
        else:
            await ctx.send("❌ No music is playing!")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
