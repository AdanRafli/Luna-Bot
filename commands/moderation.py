import discord
from discord.ext import commands
import asyncio
import random
import json
import os

XP_FILE = "xp_data.json"

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {}
    return {}

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f)

xp_data = load_xp()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    async def createrole(self, ctx, name: str, color: discord.Color = None, mentionable: bool = False, *permissions):
        guild = ctx.guild
        perms = discord.Permissions.none()
        perms.send_messages = True
        perms.read_messages = True
        perms.connect = True
        perms.speak = True

        if color is None:
            color = discord.Color.default()

        permission_map = {
            "admin": "administrator",
            "kick": "kick_members",
            "ban": "ban_members",
            "manage_roles": "manage_roles",
            "manage_channels": "manage_channels",
            "view_audit": "view_audit_log",
            "send_messages": "send_messages",
            "manage_messages": "manage_messages",
            "mute_members": "mute_members",
            "deafen_members": "deafen_members",
            "move_members": "move_members",
            "mention_everyone": "mention_everyone",
            "connect": "connect",
            "speak": "speak"
        }

        for perm in permissions:
            if perm in permission_map:
                setattr(perms, permission_map[perm], True)

        role = await guild.create_role(name=name, color=color, mentionable=mentionable, permissions=perms)
        await ctx.send(f"✅ Role `{name}` created successfully!")

    # ======================== FITUR MODERASI ========================
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx, *, role_name: str):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await role.delete()
            await ctx.send(f"✅ Role `{role_name}` telah dihapus!")
        else:
            await ctx.send(f"⚠ Role `{role_name}` tidak ditemukan.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ {amount} pesan telah dihapus!", delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx, channel_type: str, name: str, *permissions):
        guild = ctx.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}
        permission_map = {
            "send_messages": "send_messages",
            "manage_messages": "manage_messages",
            "connect": "connect",
            "speak": "speak",
            "view_channel": "view_channel",
        }

        for perm in permissions:
            if perm in permission_map:
                overwrites[guild.default_role] = discord.PermissionOverwrite(**{permission_map[perm]: True})

        if channel_type.lower() == "text":
            await guild.create_text_channel(name, overwrites=overwrites)
        elif channel_type.lower() == "voice":
            await guild.create_voice_channel(name, overwrites=overwrites)
        else:
            await ctx.send("⚠ Tipe channel tidak valid. Gunakan `text` atau `voice`.")
            return

        await ctx.send(f"✅ Channel `{name}` berhasil dibuat!")

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
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages=False, speak=False)
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} has been muted!")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
