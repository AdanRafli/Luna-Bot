import discord
from discord.ext import commands
import random

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}  # Menyimpan karakter tiap user
        self.battle_queue = []  # Antrian pertarungan

    @commands.command()
    async def create_character(self, ctx):
        if ctx.author.id in self.players:
            await ctx.send("❌ Kamu sudah memiliki karakter!")
            return

        character = {
            "name": ctx.author.name,
            "hp": random.randint(50, 100),
            "attack": random.randint(5, 20),
            "defense": random.randint(1, 10)
        }
        self.players[ctx.author.id] = character
        await ctx.send(f"✅ Karakter {character['name']} telah dibuat!\nHP: {character['hp']} | Attack: {character['attack']} | Defense: {character['defense']}")

    @commands.command()
    async def join_battle(self, ctx):
        if ctx.author.id not in self.players:
            await ctx.send("❌ Kamu harus membuat karakter dulu dengan !create_character!")
            return

        if ctx.author.id in self.battle_queue:
            await ctx.send("❌ Kamu sudah ada di antrian!")
            return

        self.battle_queue.append(ctx.author.id)
        await ctx.send(f"✅ {ctx.author.name} bergabung ke antrian battle! ({len(self.battle_queue)} pemain)")

        if len(self.battle_queue) >= 2:
            await self.start_battle(ctx)

    async def start_battle(self, ctx):
        await ctx.send("🔥 Pertarungan dimulai! 🔥")
        while len(self.battle_queue) > 1:
            attacker_id = self.battle_queue.pop(0)
            defender_id = self.battle_queue[0]

            attacker = self.players[attacker_id]
            defender = self.players[defender_id]

            damage = max(0, attacker["attack"] - defender["defense"])
            defender["hp"] -= damage

            await ctx.send(f"⚔️ {attacker['name']} menyerang {defender['name']} dan memberikan {damage} damage! ({defender['hp']} HP tersisa)")

            if defender["hp"] <= 0:
                await ctx.send(f"💀 {defender['name']} telah kalah!")
                del self.players[defender_id]
                self.battle_queue.pop(0)

        await ctx.send(f"🏆 {self.players[self.battle_queue[0]]['name']} memenangkan pertarungan! 🎉")
        self.battle_queue.clear()

async def setup(bot):
    await bot.add_cog(Battle(bot))
