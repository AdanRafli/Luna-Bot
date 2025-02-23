import discord
from discord.ext import commands
import asyncio
import os

print("DISCORD_TOKEN:", os.getenv("DISCORD_TOKEN"))

# Mengatur intents agar bot bisa membaca pesan, mengetahui server, dan anggota
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Wajib agar bot dapat membaca isi pesan
intents.guilds = True
intents.members = True         # Untuk fitur moderasi yang membutuhkan informasi member

bot = commands.Bot(command_prefix="!", intents=intents)

# 📌 Daftar izin Discord untuk referensi dalam `!permissions`
permission_map = {
    "create_instant_invite": "Membuat undangan server.",
    "kick_members": "Mengeluarkan anggota dari server.",
    "ban_members": "Membanned anggota dari server.",
    "administrator": "Memiliki semua izin (Super Admin).",
    "manage_channels": "Mengelola channel (membuat, menghapus, mengedit).",
    "manage_guild": "Mengelola server (edit nama, ikon, dsb.).",
    "add_reactions": "Menambahkan reaksi pada pesan.",
    "view_audit_log": "Melihat log audit server.",
    "priority_speaker": "Bicara dengan prioritas di voice channel.",
    "stream": "Melakukan streaming di voice channel.",
    "view_channel": "Melihat channel teks & voice.",
    "send_messages": "Mengirim pesan dalam channel teks.",
    "send_tts_messages": "Mengirim pesan TTS (teks-ke-suara).",
    "manage_messages": "Menghapus & mengedit pesan.",
    "embed_links": "Mengirim pesan dengan embed.",
    "attach_files": "Mengunggah file ke chat.",
    "read_message_history": "Melihat riwayat pesan di channel.",
    "mention_everyone": "Mention semua anggota dengan @everyone.",
    "use_external_emojis": "Menggunakan emoji dari server lain.",
    "connect": "Terhubung ke voice channel.",
    "speak": "Berbicara di voice channel.",
    "mute_members": "Mematikan mikrofon anggota lain.",
    "deafen_members": "Menonaktifkan suara anggota lain.",
    "move_members": "Memindahkan anggota antar voice channel.",
    "use_vad": "Gunakan deteksi suara otomatis (VAD).",
    "change_nickname": "Mengubah nama panggilan sendiri.",
    "manage_nicknames": "Mengubah nama panggilan anggota lain.",
    "manage_roles": "Mengelola role server.",
    "manage_webhooks": "Mengelola webhook server.",
    "manage_emojis_and_stickers": "Mengelola emoji & stiker server."
}

# 📌 Custom Help Command
class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="📌 Daftar Perintah Bot",
            description="Gunakan `!help <perintah>` untuk info lebih lanjut.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🛠 **Moderasi**",
            value=(
                "`!createrole <nama> [warna] [mentionable] [izin]` - Buat role baru.\n"
                "**Contoh:** `!createrole VIP #FFD700 yes manage_messages`\n"
                "`!deleterole <nama>` - Hapus role.\n"
                "**Contoh:** `!deleterole VIP`\n"
                "`!renamerole <lama> <baru>` - Ganti nama role.\n"
                "**Contoh:** `!renamerole Member Elite`\n"
                "`!addrole <user> <role>` - Tambahkan role ke user.\n"
                "**Contoh:** `!addrole @Andi VIP`\n"
                "`!removerole <user> <role>` - Hapus role dari user.\n"
                "**Contoh:** `!removerole @Andi VIP`\n"
                "`!kick <user> [alasan]` - Kick user.\n"
                "**Contoh:** `!kick @Andi Spam`\n"
                "`!ban <user> [alasan]` - Ban user.\n"
                "**Contoh:** `!ban @Andi Toxic`\n"
                "`!mute <user>` - Mute user (membuat role `Muted`).\n"
                "**Contoh:** `!mute @Andi`"
            ), 
            inline=False
        )

        embed.add_field(
            name="🎚 **Leveling**",
            value=(
                "`!level [user]` - Cek level user.\n"
                "**Contoh:** `!level @Andi`\n"
                "`!leaderboard` - Lihat top 10 user dengan XP tertinggi."
            ), 
            inline=False
        )

        embed.add_field(
            name="🧹 **Pesan**",
            value=(
                "`!clear <jumlah>` - Hapus beberapa pesan sebelumnya.\n"
                "**Contoh:** `!clear 10` (Menghapus 10 pesan terakhir)"
            ), 
            inline=False
        )

        embed.add_field(
            name="📢 **Channel Management**",
            value=(
                "`!createchannel <nama> [tipe] [kategori] [izin]` - Buat channel baru dengan pengaturan khusus.\n"
                "**Tipe:** `text` atau `voice`\n"
                "**Contoh:** `!createchannel diskusi text General view_channel,send_messages`\n"
                "**Contoh:** `!createchannel VC_Gaming voice Gaming connect,speak`"
            ), 
            inline=False
        )

        embed.add_field(
            name="🔑 **Daftar Izin (Permissions)**",
            value="Gunakan `!permissions` untuk melihat daftar izin lengkap!",
            inline=False
        )

        embed.set_footer(text="Gunakan !help <perintah> untuk detail lebih lanjut.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"ℹ Perintah: {command.name}",
            description=command.help or "Tidak ada deskripsi.",
            color=discord.Color.green()
        )
        await self.get_destination().send(embed=embed)

# Nonaktifkan default help command dan pasang yang baru
bot.help_command = CustomHelpCommand()

# 📌 Perintah untuk melihat daftar izin
@bot.command(name="permissions", help="Menampilkan daftar izin dan deskripsi.")
async def permissions(ctx):
    embed = discord.Embed(
        title="🔑 Daftar Izin Discord",
        description="Berikut daftar izin yang bisa digunakan untuk role & channel.",
        color=discord.Color.gold()
    )

    for perm, desc in permission_map.items():
        embed.add_field(name=perm, value=desc, inline=False)

    await ctx.send(embed=embed)

# 📌 Event saat bot online
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")

# 📌 Memuat semua extension dari folder `commands/`
async def load_extensions():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            extension = f"commands.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                print(f"✅ Loaded: {extension}")
            except Exception as e:
                print(f"❌ Failed to load {extension}: {e}")

# 📌 Main Function
async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

# 📌 Jalankan bot
if __name__ == "__main__":
    asyncio.run(main())
