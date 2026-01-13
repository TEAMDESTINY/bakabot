# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER RYAN.PY - FULL PRODUCTION READY (ALL COMMANDS REGISTERED)

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
app = Flask(__name__)

@app.route('/')
def health(): 
    return "Destiny Engine Active! 🚀"

def run_flask(): 
    from baka.config import PORT
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- INTERNAL PLUGINS IMPORT ---
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

# --- STYLIZED MENU BUTTON SYNC ---
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

# --- MAIN ENGINE STARTUP ---
if __name__ == '__main__':
    # Flask thread starts before bot to prevent health-check timeouts
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # 1. 🌹 Core & Welcome Handlers
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("welcome", welcome.welcome_command))

        # 2. 🔐 ADMIN & SUDO (Full List - Unfree Removed)
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("sudolist", admin.sudolist))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))

        # 3. 💰 ECONOMY (HTML - No Tap-to-Copy)
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("daily", economy.daily_bonus)) 
        app_bot.add_handler(CommandHandler("toprich", economy.toprich))   
        app_bot.add_handler(CommandHandler("myrank", economy.my_rank))    
        app_bot.add_handler(CommandHandler("topkill", economy.top_kill))
        app_bot.add_handler(CommandHandler("give", economy.give))

        # 4. ⚔️ GAME (Combat & Revive - HTML Style)
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob)) 
        app_bot.add_handler(CommandHandler("revive", game.revive)) #
        app_bot.add_handler(CommandHandler("protect", game.protect))

        # 5. 🧠 FUN & INFO (REGISTERED: /brain, /id)
        app_bot.add_handler(CommandHandler("brain", fun.brain)) # 0-100 range
        app_bot.add_handler(CommandHandler("id", fun.get_id))   # User/Group IDs
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))
        app_bot.add_handler(CommandHandler("slap", fun.slap))
        app_bot.add_handler(CommandHandler("punch", fun.punch))
        app_bot.add_handler(CommandHandler("hug", fun.hug))
        app_bot.add_handler(CommandHandler("kiss", fun.kiss))

        # 6. 📈 System Listeners
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CommandHandler("open", events.open_economy)) 
        app_bot.add_handler(CommandHandler("close", events.close_economy)) 

        print(f"🚀 {BOT_NAME} MASTER ENGINE ONLINE!")
        app_bot.run_polling(drop_pending_updates=True)
