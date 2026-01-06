import time
import psutil
from pyrogram import Client, filters
from bot.utils.database import db
from bot.utils.human_readable import humanbytes
from bot.info import Config

# Uptime
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
    msg = await message.reply("🔄 **Fetching Data...**", quote=True)
    
    # 1. System Stats
    cpu_per = psutil.cpu_percent()
    cpu_count = psutil.cpu_count()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    # 2. Database Stats (Global Files)
    total_files, total_bytes = await db.get_total_storage()
    
    # 3. 🔥 Streamer Bandwidth (Persistent from DB) 🔥
    # আমরা streamer_bandwidth কালেকশন থেকে ডাটা আনছি
    bw_data = await db.config_col.find_one({'_id': 'streamer_bandwidth'})
    
    if bw_data:
        ul_bytes = bw_data.get('upload', 0)
        dl_bytes = bw_data.get('download', 0)
    else:
        ul_bytes = 0
        dl_bytes = 0
        
    server_upload = humanbytes(ul_bytes)
    server_download = humanbytes(dl_bytes)
    
    # 4. Uptime & Disk
    uptime = get_readable_time(time.time() - BOT_START_TIME)

    stats_text = (
        f"🤖 **Streamer Server Stats** (Persistent)\n\n"
        f"⏳ **Uptime:** `{uptime}`\n"
        f"💻 **CPU:** `{cpu_per}%` | **RAM:** `{mem.percent}%`\n"
        f"💾 **Disk Free:** `{humanbytes(disk.free)}`\n\n"

        f"☁️ **Telegram Files:** `{total_files}`\n\n"

        f"📡 **Monthly Traffic (This Server):**\n"
        f"⬆️ **Streamed:** `{server_upload}`\n"
        f"⬇️ **Fetched:** `{server_download}`"
    )
    
    await msg.edit(stats_text)
