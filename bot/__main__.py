import os
import sys
import logging
import asyncio
from pyrogram import Client, idle
from aiohttp import web
from bot.info import Config
from bot.utils.database import db
from bot.utils.stream_helper import media_streamer 
from bot.utils.human_readable import humanbytes 

# Root Path Fix
sys.path.append(os.getcwd())

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- 🌐 WEB SERVER ROUTES ---
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route(request):
    return web.json_response({"status": "Streamer Online", "maintainer": "AnimeToki"})

@routes.get("/dl/{file_id}")
@routes.get("/watch/{file_id}")
@routes.get("/stream/{file_id}")
async def stream_handler(request):
    try:
        file_id = request.match_info['file_id']
        
        # ১. ডাটাবেস থেকে ফাইল খোঁজা
        file_data = await db.get_file(file_id)
        if not file_data:
            return web.Response(text="❌ File Not Found in Database!", status=404)
        
        db_file_name = file_data.get('file_name')
        locations = file_data.get('locations', [])

        # Fallback for old DB data
        if not locations and file_data.get('msg_id'):
            locations.append({
                'chat_id': Config.BIN_CHANNEL_1,
                'message_id': file_data.get('msg_id')
            })

        src_msg = None
        bot = request.app['bot']

        # ২. ফাইলটি চ্যানেল থেকে খুঁজে বের করা
        for loc in locations:
            chat_id = loc.get('chat_id')
            msg_id = loc.get('message_id')
            if not chat_id or not msg_id: continue
            
            try:
                msg = await bot.get_messages(chat_id, msg_id)
                if msg and (msg.document or msg.video or msg.audio):
                    src_msg = msg
                    break 
            except Exception as e:
                logger.warning(f"⚠️ Channel Access Error {chat_id}: {e}")
                continue
        
        if not src_msg:
            return web.Response(text="❌ File Missing from Channel! (Revoked/Deleted)", status=410)

        # ৩. স্ট্রিম শুরু করা
        return await media_streamer(request, src_msg, custom_file_name=db_file_name)

    except Exception as e:
        logger.error(f"Stream Error: {e}")
        return web.Response(text=f"Server Error: {e}", status=500)

# --- 🔥 MAIN STARTUP ---
async def start_streamer():
    # Pyrogram Client (No Updates Mode)
    # no_updates=True মানে এটি কোনো মেসেজ রিড করবে না, শুধু সার্ভার হিসেবে কাজ করবে
    bot = Client(
        "StreamerBot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        no_updates=True, 
        in_memory=True,
        sleep_threshold=300
    )

    app = web.Application(client_max_size=30000000)
    app.add_routes(routes)
    app['bot'] = bot

    logger.info("🚀 Starting Streamer Bot...")
    await bot.start()

    # Channel Check
    try:
        if Config.BIN_CHANNEL_1:
            await bot.get_chat(Config.BIN_CHANNEL_1)
            logger.info("✅ Connected to Bin Channel")
    except Exception as e:
        logger.error(f"❌ Bin Channel Error: {e}")

    # Web Server Start
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, Config.BIND_ADRESS, Config.PORT)
    await site.start()
    
    logger.info(f"🌐 Streamer Running at: http://{Config.BIND_ADRESS}:{Config.PORT}")
    
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_streamer())
    except KeyboardInterrupt:
        pass
