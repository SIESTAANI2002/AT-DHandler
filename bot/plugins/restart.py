import os
import sys
import asyncio
from pyrogram import Client, filters
from bot.info import Config

@Client.on_message(filters.command("restart") & filters.user(Config.OWNER_ID))
async def restart_handler(bot, message):
    # ১. ইউজারকে জানানো
    msg = await message.reply_text("🔄 **Streamer Server Restarting...**", quote=True)
    
    # ২. রিস্টার্ট মেসেজ সেভ করা (যাতে পরে এডিট করা যায়)
    restart_file = os.path.join(os.getcwd(), ".restartmsg")
    with open(restart_file, "w") as f:
        f.write(f"{msg.chat.id}\n{msg.id}")
    
    # ৩. ২ সেকেন্ড অপেক্ষা (ফাইল সেভ হওয়ার জন্য)
    await asyncio.sleep(2)
    
    # ৪. সিস্টেম রিস্টার্ট
    await msg.edit_text("🔄 **Rebooting...**")
    os.execl(sys.executable, sys.executable, *sys.argv)
