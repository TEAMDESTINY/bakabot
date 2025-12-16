# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Fixed Sudo Handlers & Aesthetic Font Sync

import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

from threading import Thread
from flask import Flask
from telegram import Update 
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    ChatMemberHandler, MessageHandler, filters
)
from telegram.request import HTTPXRequest

# --- INTERNAL IMPORTS ---
from baka.config import TOKEN, PORT
from baka.utils import log_to_channel, BOT_NAME

# Import all plugins
from baka.plugins import (
    start, economy, game, admin, broadcast, fun, events, welcome, 
    ping, chatbot, riddle, social, ai_media, waifu, collection, 
    shop, daily, leaderboard, group_econ 
)

# --- FLASK SERVER ---
app = Flask(__name__)
@app.route('/')
def health(): return "Alive"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- STARTUP LOGIC ---
async def post_init(application):
    print("✅ ᴅєsᴛɪηʏ ᴄσηєᴄᴛєᴅ!")
    await application.bot.set_my_commands([
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("help", "📖 ᴄσϻϻᴧηᴅ ᴅɪᴧꝛʏ"),
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("topgroups", "🏆 ɢꝛσυᴘ ʟєᴧᴅєꝛʙσᴧꝛᴅ"),
        ("shop", "🛒 sʜσᴘ"),
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("daily", "📅 ᴅᴧɪʟʏ"),
        ("ping", "📶 sᴛᴧᴛυs")
    ])

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: BOT_TOKEN is missing.")
    else:
        t_request = HTTPXRequest(connection_pool_size=20, connect_timeout=60.0, read_timeout=60.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # --- 1. BASIC & SYSTEM ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CallbackQueryHandler(ping.ping_callback, pattern="^sys_stats$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^return_start$"))

        # --- 2. ECONOMY & GROUPS ---
        app_bot.add_handler(CommandHandler("register", economy.register))
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("topgroups", group_econ.top_groups))
        app_bot.add_handler(CallbackQueryHandler(group_econ.top_groups, pattern="^topg_"))

        # --- 3. GAME & SHOP ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))
        app_bot.add_handler(CallbackQueryHandler(shop.shop_callback, pattern="^shop_"))

        # --- 4. ADMIN & SUDO (FIXED SECTION) ---
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("sudolist", admin.sudolist))
        app_bot.add_handler(CommandHandler("resetstats", admin.reset_stats))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("update", admin.update_bot))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        
        # IMPORTANT: Callback for Sudo Yes/No buttons
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern="^cnf|"))

        # --- 5. MESSAGE LISTENERS ---
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))
        
        # XP & Activity Tracker
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, economy.check_chat_xp), group=1)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=2)
        app_bot.add_handler(MessageHandler((filters.TEXT | filters.Sticker.ALL) & ~filters.COMMAND, chatbot.ai_message_handler), group=3)

        print("ᴅєsᴛɪηʏ ʙσᴛ ɪs ʟɪᴠє! 🚀")
        app_bot.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
