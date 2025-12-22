# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Full Menu & Handler Sync

import os
import logging
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    ChatMemberHandler, MessageHandler, filters, ContextTypes
)
from telegram.request import HTTPXRequest

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from baka.config import TOKEN, PORT
    from baka.utils import log_to_channel, BOT_NAME, stylize_text
    from baka.plugins import (
        start, economy, game, admin, broadcast, fun, events, welcome, 
        ping, chatbot, riddle, social, ai_media, waifu, collection, 
        shop, daily, leaderboard, group_econ 
    )
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    exit(1)

app = Flask(__name__)
@app.route('/')
def health(): return "Destiny Engine Active! 🚀"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- 🚀 UPDATED STARTUP MENU ---
async def post_init(application):
    commands = [
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("ranking", "🏆 ᴛσᴘ ʀɪᴄʜєsᴛ"),
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("revive", "❤️ Ꝛєᴠɪᴠє"),
        ("daily", "📅 ᴅᴧɪʟʏ ꝚєᴡᴧꝚᴅ"),
        ("shop", "🛒 sʜσᴘ"),
        ("claim", "🏰 ᴄʟᴧɪϻ ɢꝚσυᴘ"),
        ("slap", "🖐️ sʟᴧᴘ"),
        ("hug", "🫂 ʜυɢ"),
        ("kiss", "💋 ᴋɪss"),
        ("punch", "👊 ᴘυηᴄʜ"),
        ("waifu", "👗 ᴡᴧɪғυ")
    ]
    await application.bot.set_my_commands(commands)
    print(f"🚀 {BOT_NAME} is Live and Menu is Synchronized!")

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # Core
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        
        # Econ
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("daily", daily.daily)) 
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))
        app_bot.add_handler(CommandHandler("buy", shop.buy))
        
        # Game
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))

        # Fun & Social
        app_bot.add_handler(CommandHandler("slap", fun.slap))
        app_bot.add_handler(CommandHandler("hug", fun.hug))
        app_bot.add_handler(CommandHandler("kiss", fun.kiss))
        app_bot.add_handler(CommandHandler("punch", fun.punch))
        app_bot.add_handler(CommandHandler("waifu", waifu.waifu_cmd))
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle))

        # Admin
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_view|"))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        
        # Events
        app_bot.add_handler(CommandHandler("claim", events.claim_group))
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)

        app_bot.run_polling(drop_pending_updates=True)
