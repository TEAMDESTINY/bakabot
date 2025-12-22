# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Stable & Fixed Attribute Errors

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

# Error noise control
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- INTERNAL IMPORTS ---
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

# --- FLASK SERVER ---
app = Flask(__name__)
@app.route('/')
def health(): return "Destiny Engine Active! 🚀"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- STARTUP LOGIC ---
async def post_init(application):
    """Refreshes command list on startup."""
    commands = [
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("ranking", "🏆 ᴛσᴘ ʀɪᴄʜᴇsᴛ"),
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("revive", "❤️ Ꝛєᴠɪᴠє"),
        ("claim", "🏰 ᴄʟᴧɪϻ ɢꝚσυᴘ")
    ]
    await application.bot.set_my_commands(commands)
    print(f"🚀 {BOT_NAME} is Live!")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        
        app_bot = (
            ApplicationBuilder()
            .token(TOKEN)
            .request(t_request)
            .post_init(post_init)
            .build()
        )

        # --- 1. CORE ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        
        # --- 2. ECONOMY ---
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("give", economy.give))
        
        # --- 3. RPG & GAMES (FIXED HANDLERS) ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        
        # 🔥 ERROR FIX: Sirf tab add karein agar game.py mein function maujud ho
        if hasattr(game, 'check_protection_cmd'):
            app_bot.add_handler(CommandHandler("checkprotection", game.check_protection_cmd))
        if hasattr(game, 'approve_inspector'):
            app_bot.add_handler(CommandHandler("approve", game.approve_inspector))

        # --- 4. ADMIN & CALLBACKS ---
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern="^cnf|"))
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_view|"))
        app_bot.add_handler(CommandHandler("claim", events.claim_group))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))

        # --- 5. LISTENERS ---
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))

        app_bot.run_polling(drop_pending_updates=True)
