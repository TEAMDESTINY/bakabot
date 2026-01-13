# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL FIXED MASTER RYAN.PY - NO NAMEERROR

import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ChatMemberHandler, filters, PrefixHandler
)
from telegram.request import HTTPXRequest

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FLASK SERVER (Uptime Monitoring) ---
# Iska definition upar hona chahiye taaki startup par NameError na aaye
app = Flask(__name__)

@app.route('/')
def health(): 
    return "Destiny Engine Active! 🚀"

def run_flask(): 
    # Flask ko correctly run karne ka function
    from baka.config import PORT
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- INTERNAL IMPORTS ---
try:
    from baka.config import TOKEN, PORT
    from baka.utils import BOT_NAME
    
    import baka.plugins.start as start
    import baka.plugins.economy as economy
    import baka.plugins.game as game
    import baka.plugins.admin as admin
    import baka.plugins.broadcast as broadcast
    import baka.plugins.fun as fun
    import baka.plugins.events as events
    import baka.plugins.ping as ping
    import baka.plugins.chatbot as chatbot
    import baka.plugins.welcome as welcome

except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    exit(1)

# --- STYLIZED STARTUP MENU ---
async def post_init(application):
    commands = [
        ("start", "Start System 🌹"), 
        ("bal", "Wallet Balance 🌹"), 
        ("toprich", "Rich Board 🌹"), 
        ("kill", "Kill Someone 🌹"), 
        ("rob", "Steal Money 🌹"),
        ("brain", "Check IQ 🧠"),
        ("id", "Get IDs 🆔"),
        ("sudo", "Sudo Panel 🔐")
    ]
    await application.bot.set_my_commands(commands)

# --- MAIN ENGINE ---
if __name__ == '__main__':
    # Flask thread starting
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # 1. Core Handlers
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("welcome", welcome.welcome_command))

        # 2. 🔐 ADMIN COMMANDS (FULL LIST REGISTERED)
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))

        # 3. 💰 ECONOMY (Synced)
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("daily", economy.daily_bonus)) 
        app_bot.add_handler(CommandHandler("toprich", economy.toprich))   
        app_bot.add_handler(CommandHandler("myrank", economy.my_rank))    
        app_bot.add_handler(CommandHandler("topkill", economy.top_kill))

        # 4. ⚔️ GAME (Synced)
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob)) 
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))

        # 5. 🧠 FUN & INFO (REGISTERED)
        app_bot.add_handler(CommandHandler("brain", fun.brain)) # IQ calculation
        app_bot.add_handler(CommandHandler("id", fun.get_id))   # ID retrieval
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))

        print(f"🚀 {BOT_NAME} MASTER ENGINE ONLINE!")
        app_bot.run_polling(drop_pending_updates=True)
