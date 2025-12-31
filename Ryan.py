# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER RYAN.PY - FULL ECONOMY & GIFTING SYNC

import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters
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
        ping, chatbot, riddle, waifu, shop, couple 
    )
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    exit(1)

# --- FLASK SERVER (Uptime Monitoring) ---
app = Flask(__name__)
@app.route('/')
def health(): return "Destiny Engine Active! 🚀"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- STARTUP MENU ---
async def post_init(application):
    """Syncs the full command list to the bot menu."""
    commands = [
        ("start", "🌸 Main Menu"), 
        ("help", "📖 Help Guide"),
        ("bal", "👛 Wallet Balance"), 
        ("toprich", "🏆 Rich Leaderboard"), 
        ("topkill", "⚔️ Kill Leaderboard"),
        ("daily", "📅 12h Reward"),
        ("kill", "🔪 Kill Someone"), 
        ("rob", "💰 Steal Money"),
        ("items", "🛒 Gift Shop"),
        ("item", "📦 My Inventory"),
        ("myrank", "🏆 Global Rank"),
        ("economy", "📖 Economy Guide")
    ]
    await application.bot.set_my_commands(commands)
    print(f"✅ {BOT_NAME} Absolute Menu Synchronized!")

# --- MAIN ENGINE ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # 1. Core & Help Callbacks
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("economy", start.help_command))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_|return_start"))

        # 2. 🔐 Admin & Sudo
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))

        # 3. Economy & Gifting System
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("daily", economy.daily_bonus)) 
        app_bot.add_handler(CommandHandler("toprich", economy.toprich))   
        app_bot.add_handler(CommandHandler("myrank", economy.my_rank))    
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("topkill", economy.top_kill)) # Added
        
        # Shop & Items
        app_bot.add_handler(CommandHandler("items", shop.items_list))   # Added
        app_bot.add_handler(CommandHandler("item", shop.view_inventory)) # Added
        app_bot.add_handler(CommandHandler("gift", shop.gift_item))      # Added

        # 4. Game & Combat
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob)) 
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))

        # 5. Chatbot, AI & Fun
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chatbot.ai_message_handler))
        app_bot.add_handler(CommandHandler("couple", couple.couple)) 
        app_bot.add_handler(CommandHandler("waifu", waifu.waifu_cmd)) 
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle))
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))

        # 6. Listeners
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)

        print(f"🚀 {BOT_NAME} IS FULLY SYNCED AND ONLINE!")
        app_bot.run_polling(drop_pending_updates=True)
