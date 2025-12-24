# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER RYAN.PY - ADMIN & PLUGINS SYNCED

import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    ChatMemberHandler, MessageHandler, filters
)
from telegram.request import HTTPXRequest

# Error noise control
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- INTERNAL IMPORTS ---
try:
    from baka.config import TOKEN, PORT
    from baka.utils import BOT_NAME
    from baka.plugins import (
        start, economy, game, admin, broadcast, fun, events, 
        ping, chatbot, riddle, waifu, daily, leaderboard, shop,
        couple 
    )
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    exit(1)

# --- FLASK SERVER (Uptime) ---
app = Flask(__name__)
@app.route('/')
def health(): return "Destiny Engine Active! 🚀"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- STARTUP MENU ---
async def post_init(application):
    commands = [
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("top", "🏆 ʟєᴧᴅєꝚʙσᴧꝚᴅ"), 
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("daily", "📅 ᴅᴧɪʟʏ ꝚєᴡᴧꝚᴅ"),
        ("couple", "👩‍❤️‍👨 ᴄσυᴘʟє"),
        ("waifu", "👗 ᴡᴧɪғυ")
    ]
    await application.bot.set_my_commands(commands)
    print(f"✅ {BOT_NAME} Menu Synchronized!")

# --- MAIN ENGINE ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # 1. Core & Admin Commands (Fixed)
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help)) # Admin Panel
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins)) # Add Money
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb)) # Clear Data
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))

        # 2. Economy & Games
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("daily", daily.daily)) 
        app_bot.add_handler(CommandHandler("top", leaderboard.leaderboard)) 
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))

        # 3. Fun, Social & Couple
        app_bot.add_handler(CommandHandler("slap", fun.slap))
        app_bot.add_handler(CommandHandler("punch", fun.punch))
        app_bot.add_handler(CommandHandler("hug", fun.hug))
        app_bot.add_handler(CommandHandler("kiss", fun.kiss))
        app_bot.add_handler(CommandHandler("couple", couple.couple)) 
        app_bot.add_handler(CommandHandler("waifu", waifu.waifu_cmd)) 
        app_bot.add_handler(CommandHandler("propose", waifu.wpropose))
        app_bot.add_handler(CommandHandler("marry", waifu.wmarry))
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle))

        # 4. Global Anime Actions
        if hasattr(waifu, 'SFW_ACTIONS'):
            for act in waifu.SFW_ACTIONS:
                app_bot.add_handler(CommandHandler(act, waifu.waifu_action))

        # 5. Listeners
        app_bot.add_handler(CommandHandler("claim", events.claim_group))
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & (~filters.COMMAND), riddle.check_riddle_answer), group=1)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)

        print(f"--------------------------")
        print(f"🚀 {BOT_NAME} ENGINE STARTED!")
        print(f"--------------------------")
        
        app_bot.run_polling(drop_pending_updates=True)
