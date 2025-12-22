# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Fully Integrated & Fixed Handlers

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
        ("daily", "📅 ᴅᴧɪʟʏ ꝚєᴡᴧꝚᴅ"),
        ("shop", "🛒 sʜσᴘ"),
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

        # --- 1. CORE COMMANDS ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        
        # --- 2. ECONOMY & SHOP ---
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("daily", daily.daily_claim))
        app_bot.add_handler(CommandHandler("shop", shop.open_shop))
        app_bot.add_handler(CommandHandler("buy", shop.buy_item))
        app_bot.add_handler(CommandHandler("top", leaderboard.show_leaderboard))
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_view|"))
        
        # --- 3. RPG & GAMES ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        if hasattr(game, 'check_protection_cmd'):
            app_bot.add_handler(CommandHandler("checkprotection", game.check_protection_cmd))

        # --- 4. FUN & SOCIAL (Yahan aapke fun commands hain) ---
        app_bot.add_handler(CommandHandler("slap", fun.slap))
        app_bot.add_handler(CommandHandler("hug", fun.hug))
        app_bot.add_handler(CommandHandler("kiss", fun.kiss))
        app_bot.add_handler(CommandHandler("punch", fun.punch))
        app_bot.add_handler(CommandHandler("bite", fun.bite))
        app_bot.add_handler(CommandHandler("pat", fun.pat))
        app_bot.add_handler(CommandHandler("waifu", waifu.get_waifu))
        app_bot.add_handler(CommandHandler("riddle", riddle.get_riddle))

        # --- 5. ADMIN & OWNER ONLY ---
        app_bot.add_handler(CommandHandler("sudohelp", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("sudolist", admin.sudolist))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        
        # IMPORTANT: Admin confirmation callbacks
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))

        # --- 6. LISTENERS & EVENTS ---
        app_bot.add_handler(CommandHandler("claim", events.claim_group))
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        
        # Chatbot (Optional toggle)
        app_bot.add_handler(CommandHandler("chatbot", chatbot.toggle_chatbot))

        print("✅ All Handlers Loaded Successfully!")
        app_bot.run_polling(drop_pending_updates=True)
