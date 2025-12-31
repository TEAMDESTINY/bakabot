# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER RYAN.PY - ABSOLUTE INTEGRATION

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
        ping, chatbot, riddle, waifu, daily, leaderboard, shop,
        couple 
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
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("help", "📖 𝖧𝖤𝖫𝖯"),
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("top", "🏆 ʟєᴧᴅєꝚʙσᴧꝚᴅ"), 
        ("daily", "📅 ᴅᴧɪʟʏ ꝚєᴡᴧꝚᴅ"),
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("couple", "👩‍❤️‍👨 ᴄσυᴘʟє"),
        ("sudo", "🔐 𝖲𝖴𝖣𝖮 𝖯𝖠𝖭𝖤𝖫")
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
        # Logic for help menu navigation
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_|return_start"))

        # 2. 🔐 Full Admin & Sudo Registration
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("sudolist", admin.sudolist))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        # Handler for admin confirmation buttons
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))

        # 3. Economy & RPG (Custom Amount Rob Registered)
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("daily", daily.daily)) 
        app_bot.add_handler(CommandHandler("top", leaderboard.leaderboard)) 
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob)) # Custom amount rob sync
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))

        # 4. Chatbot & AI Integration
        app_bot.add_handler(CommandHandler("chatbot", chatbot.chatbot_menu))
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))
        app_bot.add_handler(CallbackQueryHandler(chatbot.chatbot_callback, pattern="^ai_"))
        # Main AI logic for text replies
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chatbot.ai_message_handler))

        # 5. Fun, Social & Couple
        app_bot.add_handler(CommandHandler("couple", couple.couple)) 
        app_bot.add_handler(CommandHandler("waifu", waifu.waifu_cmd)) 
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle))
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))

        # 6. Listeners
        app_bot.add_handler(CommandHandler("claim", events.claim_group))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & (~filters.COMMAND), riddle.check_riddle_answer), group=1)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)

        print(f"🚀 {BOT_NAME} IS FULLY SYNCED AND ONLINE!")
        app_bot.run_polling(drop_pending_updates=True)
