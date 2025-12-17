# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Stable, Multi-Feature & Error-Free Polling

import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    ChatMemberHandler, MessageHandler, filters
)
from telegram.request import HTTPXRequest

# Set environment for GitPython to avoid noise
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- INTERNAL IMPORTS ---
try:
    from baka.config import TOKEN, PORT
    from baka.utils import log_to_channel, BOT_NAME
    from baka.plugins import (
        start, economy, game, admin, broadcast, fun, events, welcome, 
        ping, chatbot, riddle, social, ai_media, waifu, collection, 
        shop, daily, leaderboard, group_econ 
    )
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    exit(1)

# --- FLASK SERVER (Uptime Monitoring) ---
# Keeps the bot alive on services like Render, Heroku, or Koyeb
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is Running!"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- STARTUP LOGIC ---
async def post_init(application):
    """Executes once the bot starts successfully."""
    print("✅ BOT CONNECTED! SETTING MENU COMMANDS...")
    
    commands = [
        ("start", "🌸 Main Menu"), 
        ("help", "📖 Command Diary"),
        ("bal", "👛 Wallet"), 
        ("shop", "🛒 Shop"),
        ("kill", "🔪 Kill"), 
        ("rob", "💰 Steal"), 
        ("give", "💸 Transfer"), 
        ("claim", "💎 Bonus"),
        ("daily", "📅 Daily"), 
        ("ranking", "🏆 Top Players"),
        ("propose", "💍 Marry"), 
        ("divorce", "💔 Breakup"),
        ("wpropose", "👰 Waifu"), 
        ("draw", "🎨 AI Art"),
        ("speak", "🗣️ Voice"), 
        ("chatbot", "🧠 AI Chat"),
        ("ping", "📶 Status")
    ]
    
    await application.bot.set_my_commands(commands)
    
    try:
        bot_info = await application.bot.get_me()
        print(f"✅ Logged in as @{bot_info.username}")
        await log_to_channel(application.bot, "start", {
            "user": "System", 
            "chat": "Cloud Server",
            "action": f"{BOT_NAME} is now Online! 🚀"
        })
    except Exception as e:
        logger.error(f"Startup Log Failed: {e}")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Start the web server in a background thread
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL ERROR: BOT_TOKEN is missing in config.")
    else:
        # High-performance network config for handling high traffic
        t_request = HTTPXRequest(
            connection_pool_size=25, 
            connect_timeout=30.0, 
            read_timeout=30.0
        )
        
        app_bot = (
            ApplicationBuilder()
            .token(TOKEN)
            .request(t_request)
            .post_init(post_init)
            .build()
        )

        # --- REGISTER HANDLERS ---
        
        # 1. Basics & Navigation
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CallbackQueryHandler(ping.ping_callback, pattern="^sys_stats$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^return_start$"))
        
        # 2. Economy & Commerce
        app_bot.add_handler(CommandHandler("register", economy.register))
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("claim", economy.claim))
        app_bot.add_handler(CommandHandler("daily", daily.daily))
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))
        app_bot.add_handler(CommandHandler("buy", shop.buy))
        app_bot.add_handler(CallbackQueryHandler(shop.shop_callback, pattern="^shop_"))
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_"))
        
        # 3. RPG / Combat Game
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        
        # 4. Social & Waifu System
        app_bot.add_handler(CommandHandler("propose", social.propose))
        app_bot.add_handler(CommandHandler("marry", social.marry_status))
        app_bot.add_handler(CommandHandler("divorce", social.divorce))
        app_bot.add_handler(CommandHandler("couple", social.couple_game))
        app_bot.add_handler(CallbackQueryHandler(social.proposal_callback, pattern="^marry_"))
        
        app_bot.add_handler(CommandHandler("wpropose", waifu.wpropose))
        app_bot.add_handler(CommandHandler("wmarry", waifu.wmarry))
        for action in waifu.SFW_ACTIONS:
            app_bot.add_handler(CommandHandler(action, waifu.waifu_action))

        # 5. Fun / AI / Media
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle_command))
        app_bot.add_handler(CommandHandler("draw", ai_media.draw_command))
        app_bot.add_handler(CommandHandler("speak", ai_media.speak_command))
        app_bot.add_handler(CommandHandler("chatbot", chatbot.chatbot_menu)) 
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))           
        app_bot.add_handler(CallbackQueryHandler(chatbot.chatbot_callback, pattern="^ai_")) 
        
        # 6. Admin & Sudo Controls
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("sudolist", admin.sudolist))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("update", admin.update_bot))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern="^cnf|"))
        
        # 7. Group Analytics
        app_bot.add_handler(CommandHandler("topgroups", group_econ.top_groups))
        app_bot.add_handler(CallbackQueryHandler(group_econ.top_groups, pattern="^topg_"))

        # 8. Events & Background Message Listeners
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))
        
        # Grouped Message Handling (Ordered by Priority)
        # Group 1: Waifu Collection logic
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, collection.collect_waifu), group=1)
        # Group 2: Item Drops logic
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, collection.check_drops), group=2)
        # Group 3: Riddle Solver logic
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, riddle.check_riddle_answer), group=3)
        # Group 4: AI Chatbot (Global Responder)
        app_bot.add_handler(MessageHandler((filters.TEXT | filters.Sticker.ALL) & ~filters.COMMAND, chatbot.ai_message_handler), group=4)
        # Group 5: Group Statistics Tracking
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=5)

        print("--------------------------")
        print("🚀 DESTINY BOT IS LIVE!")
        print("--------------------------")
        
        # Start the bot
        app_bot.run_polling(
            allowed_updates=Update.ALL_TYPES, 
            drop_pending_updates=True, 
            bootstrap_retries=5
        )
