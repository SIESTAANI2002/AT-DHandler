import asyncio
import datetime
import psutil
from bot.utils.database import db

async def bandwidth_monitor():
    # লুপ শুরুর আগে বর্তমান নেটওয়ার্ক রিডিং নেওয়া
    io = psutil.net_io_counters()
    last_sent = io.bytes_sent
    last_recv = io.bytes_recv

    while True:
        await asyncio.sleep(20) # ২০ সেকেন্ড পর পর আপডেট হবে

        try:
            # বর্তমান রিডিং
            io = psutil.net_io_counters()
            curr_sent = io.bytes_sent
            curr_recv = io.bytes_recv

            # পার্থক্য (Delta) বের করা (কতটুকু নতুন ডাটা গেল)
            sent_delta = curr_sent - last_sent
            recv_delta = curr_recv - last_recv

            # যদি সার্ভার রিস্টার্ট হয়, তাহলে নেগেটিভ ভ্যালু আসতে পারে। তখন বর্তমানটাই ডেল্টা।
            if sent_delta < 0: sent_delta = curr_sent
            if recv_delta < 0: recv_delta = curr_recv

            last_sent = curr_sent
            last_recv = curr_recv

            # যদি কোনো ডাটা আদান-প্রদান হয়, তবেই DB আপডেট হবে
            if sent_delta > 0 or recv_delta > 0:
                # 🔥 আলাদা ID তে সেভ হচ্ছে (streamer_bandwidth)
                await db.config_col.update_one(
                    {'_id': 'streamer_bandwidth'},
                    {'$inc': {'upload': sent_delta, 'download': recv_delta}},
                    upsert=True
                )

            # --- 📅 Monthly Reset Logic (শুধুমাত্র স্ট্রিমারের জন্য) ---
            now = datetime.datetime.now()
            current_month = f"{now.year}-{now.month}"
            
            # DB থেকে রিসেট ডেট চেক করা
            data = await db.config_col.find_one({'_id': 'streamer_bandwidth'})
            if data:
                saved_month = data.get('last_reset')
                if saved_month != current_month:
                    # মাস চেঞ্জ হলে ০ করে দেওয়া
                    await db.config_col.update_one(
                        {'_id': 'streamer_bandwidth'},
                        {'$set': {'upload': 0, 'download': 0, 'last_reset': current_month}}
                    )

        except Exception as e:
            print(f"Monitor Error: {e}")
