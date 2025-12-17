# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Optimized for High Traffic & Global Groups

import os
import logging
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    ChatMemberHandler, MessageHandler, filters
)
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
app = Flask(__name__)
@app.route('/')
def health(): return "Destiny Bot is Active! 🚀"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- STARTUP LOGIC ---
async def post_init(application):
    print("✅ DESTINY ENGINE CONNECTED!")
    
    commands = [
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("help", "📖 ᴄσϻϻᴧηᴅ ᴅɪᴧꝛʏ"),
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("shop", "🛒 sʜσᴘ"),
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("give", "💸 ᴛꝛᴧηsғєꝛ"), 
        ("claim", "💎 ʙσηυs"),
        ("daily", "📅 ᴅᴧɪʟʏ"), 
        ("ranking", "🏆 ᴛσᴘs"),
        ("propose", "💍 ϻᴧꝛꝛʏ"), 
        ("divorce", "💔 ʙꝛєᴧᴋυᴘ"),
        ("wpropose", "👰 ᴡᴧɪғυ"), 
        ("draw", "🎨 ᴧꝛᴛ"),
        ("speak", "🗣️ νσɪᴄє"), 
        ("chatbot", "🧠 ᴧɪ"),
        ("ping", "📶 sᴛᴧᴛυs")
    ]
    await application.bot.set_my_commands(commands)
    
    bot_info = await application.bot.get_me()
    print(f"🚀 Destiny Bot (@{bot_info.username}) is now Online!")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: BOT_TOKEN missing!")
    else:
        # High-performance request config for Group Overload protection
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

        # --- 1. CORE HANDLERS ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CallbackQueryHandler(ping.ping_callback, pattern="^sys_stats$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^return_start$"))
        
        # --- 2. ECONOMY & EMPIRE ---
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
        
        # --- 3. RPG & WARFARE ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("protect", game.protect))
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("mining", group_econ.passive_mining))
        app_bot.add_handler(CommandHandler("raid", group_econ.territory_raid))
        app_bot.add_handler(CommandHandler("stock", group_econ.stock_market))
        app_bot.add_handler(CommandHandler("governor", group_econ.ai_governor))

        # --- 4. SOCIAL & WAIFU ---
        app_bot.add_handler(CommandHandler("propose", social.propose))
        app_bot.add_handler(CommandHandler("marry", social.marry_status))
        app_bot.add_handler(CommandHandler("divorce", social.divorce))
        app_bot.add_handler(CommandHandler("couple", social.couple_game))
        app_bot.add_handler(CallbackQueryHandler(social.proposal_callback, pattern="^marry_"))
        app_bot.add_handler(CommandHandler("wpropose", waifu.wpropose))
        app_bot.add_handler(CommandHandler("wmarry", waifu.wmarry))
        for act in waifu.SFW_ACTIONS:
            app_bot.add_handler(CommandHandler(act, waifu.waifu_action))

        # --- 5. FUN & AI ---
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle_command))
        app_bot.add_handler(CommandHandler("draw", ai_media.draw_command))
        app_bot.add_handler(CommandHandler("speak", ai_media.speak_command))
        app_bot.add_handler(CommandHandler("chatbot", chatbot.chatbot_menu)) 
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))           
        app_bot.add_handler(CallbackQueryHandler(chatbot.chatbot_callback, pattern="^ai_")) 
        
        # --- 6. SYSTEM & ADMIN ---
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addsudo", admin.addsudo))
        app_bot.add_handler(CommandHandler("rmsudo", admin.rmsudo))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("cleandb", admin.cleandb))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CommandHandler("topgroups", group_econ.top_groups))
        app_bot.add_handler(CallbackQueryHandler(group_econ.top_groups, pattern="^topg_"))
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern="^cnf|"))

        # --- 7. MESSAGE LISTENERS (Ordered) ---
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))
        
        # Logic Groups (Performance optimized)
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, collection.collect_waifu), group=1)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, collection.check_drops), group=2)
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, riddle.check_riddle_answer), group=3)
        app_bot.add_handler(MessageHandler((filters.TEXT | filters.Sticker.ALL) & ~filters.COMMAND, chatbot.ai_message_handler), group=4)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=5)

        print("--------------------------")
        print("🚀 DESTINY BOT IS ONLINE!")
        print("--------------------------")
        
        app_bot.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
