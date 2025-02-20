import discord
from discord.ext import commands
import asyncio
import random
import json
import os

# Load XP data
XP_FILE = "xp_data.json"
def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

xp_data = load_xp()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.waiting_list = []  # Antrian minigame

    # ======================== SISTEM LEVEL ========================
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user_id = str(message.author.id)
        xp_data[user_id] = xp_data.get(user_id, 0) + random.randint(5, 15)
        save_xp(xp_data)

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        xp = xp_data.get(str(member.id), 0)
        level = xp // 100
        await ctx.send(f"🌟 {member.mention} is level {level} with {xp} XP!")

    @commands.command()
    async def leaderboard(self, ctx):
        sorted_xp = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)[:10]
        leaderboard_text = "\n".join([f"{ctx.guild.get_member(int(user_id))}: {xp} XP" for user_id, xp in sorted_xp])
        embed = discord.Embed(title="🏆 XP Leaderboard", description=leaderboard_text, color=discord.Color.gold())
        await ctx.send(embed=embed)

    # ======================== PEMBUATAN ROLE ========================
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, name: str, color: discord.Color = discord.Color.default()):
        guild = ctx.guild
        await guild.create_role(name=name, color=color)
        await ctx.send(f"✅ Role `{name}` created successfully!")

    # ======================== PEMBUATAN CHANNEL ========================
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx, name: str, channel_type: str = "text"):
        guild = ctx.guild
        if channel_type.lower() == "voice":
            await guild.create_voice_channel(name)
        else:
            await guild.create_text_channel(name)
        await ctx.send(f"✅ Channel `{name}` created successfully!")

    # ======================== FITUR MODERASI ========================
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.name} has been kicked!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.name} has been banned!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member_name:
                await ctx.guild.unban(user)
                await ctx.send(f"✅ {user.name} has been unbanned!")
                return

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages=False, speak=False)
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} has been muted!")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"✅ {member.mention} has been unmuted!")

    # ======================== MINIGAME WAITING LIST ========================
    @commands.command()
    async def join_game(self, ctx):
        if ctx.author.id in self.waiting_list:
            await ctx.send("❌ Kamu sudah ada di antrian minigame!")
            return
        
        self.waiting_list.append(ctx.author.id)
        await ctx.send(f"✅ {ctx.author.name} telah bergabung ke antrian minigame ({len(self.waiting_list)} pemain).")
        
        if len(self.waiting_list) >= 2:
            await self.start_game(ctx)

    async def start_game(self, ctx):
        await ctx.send("🎮 Minigame dimulai!")
        players = [self.bot.get_user(uid) for uid in self.waiting_list]
        winner = random.choice(players)
        
        await ctx.send(f"🏆 Pemenangnya adalah **{winner.name}**! 🎉")
        self.waiting_list.clear()

    # ======================== MINI GAME TEBAK ANGKA ========================
    @commands.command()
    async def guess(self, ctx):
        number = random.randint(1, 10)
        await ctx.send("🎲 Guess a number between 1 and 10!")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=10.0)
            if int(msg.content) == number:
                await ctx.send("✅ Correct! You guessed the number!")
            else:
                await ctx.send(f"❌ Wrong! The correct number was {number}.")
        except asyncio.TimeoutError:
            await ctx.send("⌛ Time's up! You didn't guess in time.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
