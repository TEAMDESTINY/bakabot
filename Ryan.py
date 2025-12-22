# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Stable, Multi-Feature & Conflict-Free

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
# Optimized Request Config for high-speed handling
from telegram.request import HTTPXRequest

# Error noise kam karne ke liye
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# --- LOGGING SETUP ---
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

# --- FLASK SERVER (Uptime Monitoring) ---
app = Flask(__name__)
@app.route('/')
def health(): return "Destiny Engine is Active! 🚀"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- 🛡️ GLOBAL ERROR HANDLER ---
async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# --- STARTUP LOGIC ---
async def post_init(application):
    """Executes once the bot starts successfully."""
    print("✅ DESTINY ENGINE CONNECTED!")
    
    # Setting up the Menu for easy navigation
    commands = [
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("help", "📖 ᴄσϻϻᴧηᴅ ᴅɪᴧꝛʏ"),
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("ranking", "🏆 ᴛσᴘ ʀɪᴄʜᴇsᴛ"),
        ("shop", "🛒 sʜσᴘ"),
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("claim", "🏰 ᴄʟᴧɪϻ ɢꝚσυᴘ"),
        ("daily", "📅 ᴅᴧɪʟʏ"), 
        ("ping", "📶 sᴛᴧᴛυs"),
        ("checkprotection", "🔍 sᴘʏ ση sʜɪєʟᴅ")
    ]
    await application.bot.set_my_commands(commands)
    bot_info = await application.bot.get_me()
    print(f"🚀 {BOT_NAME} (@{bot_info.username}) is now Online!")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Flask thread starts for keeping the bot alive
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: BOT_TOKEN is missing!")
    else:
        # High-performance HTTPX configuration
        t_request = HTTPXRequest(
            connection_pool_size=30, 
            connect_timeout=40.0, 
            read_timeout=40.0,
            write_timeout=40.0
        )
        
        app_bot = (
            ApplicationBuilder()
            .token(TOKEN)
            .request(t_request)
            .post_init(post_init)
            .build()
        )

        app_bot.add_error_handler(global_error_handler)

        # --- 1. CORE & PING ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CallbackQueryHandler(ping.ping_callback, pattern="^sys_stats$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        
        # --- 2. ECONOMY & SHOP ---
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking)) # Leaderboard fix
        app_bot.add_handler(CommandHandler("daily", daily.daily))
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))
        app_bot.add_handler(CommandHandler("buy", shop.buy))
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CallbackQueryHandler(shop.shop_callback, pattern="^shop_"))
        
        # 🔥 CALLBACK ORDER FIX: Admin handler must be prioritized
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern="^cnf|"))
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_view|"))
        
        # --- 3. RPG & GAMES ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        app_bot.add_handler(CommandHandler("approve", game.approve_inspector))
        app_bot.add_handler(CommandHandler("checkprotection", game.check_protection_cmd))
        app_bot.add_handler(CommandHandler("mining", group_econ.passive_mining))
        app_bot.add_handler(CommandHandler("raid", group_econ.territory_raid))
        
        # --- 4. SYSTEM & ADMIN ---
        app_bot.add_handler(CommandHandler("claim", events.claim_group)) # Group claiming fix
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("sudolist", admin.sudolist))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))

        # --- 5. LISTENERS ---
        # Group activity and XP listeners
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, economy.check_chat_xp), group=2)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot.ai_message_handler), group=4)

        print("--------------------------")
        print(f"🚀 {BOT_NAME} IS LIVE & SECURE!")
        print("--------------------------")
        
        app_bot.run_polling(drop_pending_updates=True)
