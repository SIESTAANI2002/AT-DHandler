import time
import psutil
from pyrogram import Client, filters
from bot.utils.database import db
from bot.utils.human_readable import humanbytes
from bot.info import Config

# Uptime Calculation
BOT_START_TIME = time.time()

def get_readable_time(seconds):
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0: result += f"{days}d "
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0: result += f"{hours}h "
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0: result += f"{minutes}m "
    seconds = int(seconds)
    result += f"{seconds}s"
    return result

@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.OWNER_ID))
async def stats_handler(bot, message):
    msg = await message.reply("🔄 **Fetching Stats...**", quote=True)
    
    # 1. System Stats
    cpu_per = psutil.cpu_percent()
    cpu_count = psutil.cpu_count() # Core Count
    mem = psutil.virtual_memory()
    ram_per = mem.percent
    total_ram = humanbytes(mem.total)
    disk = psutil.disk_usage("/")
    
    # 2. Database Stats
    total_files, total_bytes = await db.get_total_storage()
    cloud_storage = humanbytes(total_bytes)
    
    # 3. Bandwidth Stats
    db_upload, db_download = await db.get_bandwidth()
    total_ul = humanbytes(db_upload)
    total_dl = humanbytes(db_download)
    
    # 4. Uptime & Disk Space
    uptime = get_readable_time(time.time() - BOT_START_TIME)
    total_space = humanbytes(disk.total)
    free_space = humanbytes(disk.free)

    # 🔥 আপনার চাওয়া ফরম্যাট 🔥
    stats_text = (
        f"🤖 **Bot System Stats**\n\n"
        f"⏳ **Uptime:** `{uptime}`\n"
        f"💻 **CPU:** `{cpu_per}%` | **RAM:** `{ram_per}%`\n"
        f"🖥️ **Core:** `{cpu_count}` | **Total Ram:** `{total_ram}`\n\n"

        f"☁️ **Telegram Cloud Storage:**\n"
        f"📚 **Total Files:** `{total_files}`\n"
        f"📦 **Total Size:** `{cloud_storage}`\n\n"

        f"📡 **Monthly Bandwidth:**\n"
        f"⬆️ **Upload:** `{total_ul}`\n"
        f"⬇️ **Download:** `{total_dl}`\n\n"

        f"💾 **Server Disk:**\n"
        f"✅ **Free:** `{free_space}` / `{total_space}`"
    )
    
    await msg.edit(stats_text)
