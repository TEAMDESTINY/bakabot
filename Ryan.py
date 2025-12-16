# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Ryan.py - Stable & Error Free

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
    shop, daily, leaderboard, group_econ  # <== Ensure group_econ.py exists in plugins
)

# --- FLASK SERVER ---
app = Flask(__name__)
@app.route('/')
def health(): return "Alive"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- STARTUP LOGIC ---
async def post_init(application):
    print("✅ ʙᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ! ꜱᴇᴛᴛɪɴɢ ᴍᴇɴᴜ ᴄᴏᴍᴍᴀɴᴅꜱ...")

    await application.bot.set_my_commands([
        ("start", "🌸 ϻᴧɪη ϻєηυ"), 
        ("help", "📖 ᴄσϻϻᴧηᴅ ᴅɪᴧꝛʏ"),
        ("bal", "👛 ᴡᴧʟʟєᴛ"), 
        ("stock", "📈 ɢꝛσυᴘ sᴛσᴄᴋs"),
        ("raid", "⚔️ ᴛєꝛꝛɪᴛσꝛʏ ꝛᴧɪᴅ"),
        ("mining", "⛏️ ᴘᴧssɪνє ϻɪηɪηɢ"),
        ("governor", "🏛️ ᴧɪ ɢσνєꝛησꝛ"),
        ("shop", "🛒 sʜσᴘ"),
        ("kill", "🔪 ᴋɪʟʟ"), 
        ("rob", "💰 sᴛєᴧʟ"), 
        ("give", "💸 ᴛꝛᴧηsғєꝛ"), 
        ("claim", "💎 ʙσηυs"),
        ("daily", "📅 ᴅᴧɪʟʏ"),
        ("ranking", "🏆 ᴛσᴘs"),
        ("chatbot", "🧠 ᴧɪ"),
        ("ping", "📶 sᴛᴧᴛυs")
    ])

    try:
        bot_info = await application.bot.get_me()
        print(f"✅ Logged in as {bot_info.username}")
        await log_to_channel(application.bot, "start", {
            "user": "System", 
            "chat": "Cloud Server",
            "action": f"{BOT_NAME} (@{bot_info.username}) is now Online! 🚀"
        })
    except Exception as e:
        print(f"⚠️ Startup Log Failed: {e}")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    if not TOKEN:
        print("CRITICAL: BOT_TOKEN is missing.")
    else:
        t_request = HTTPXRequest(connection_pool_size=16, connect_timeout=60.0, read_timeout=60.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # --- BASIC COMMANDS ---
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(CommandHandler("help", start.help_command))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        app_bot.add_handler(CallbackQueryHandler(ping.ping_callback, pattern="^sys_stats$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^return_start$"))

        # --- ECONOMY PLUGIN HANDLERS ---
        app_bot.add_handler(CommandHandler("register", economy.register))
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("ranking", economy.ranking))
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("claim", economy.claim))
        app_bot.add_handler(CommandHandler("sellxp", economy.sell_xp))
        # Inventory Callback (Fixed)
        app_bot.add_handler(CallbackQueryHandler(economy.inventory_callback, pattern="^inv_"))

        # --- GROUP ECONOMY PLUGIN HANDLERS (New Viral Commands) ---
        app_bot.add_handler(CommandHandler("stock", group_econ.stock_market))
        app_bot.add_handler(CommandHandler("raid", group_econ.territory_raid))
        app_bot.add_handler(CommandHandler("governor", group_econ.ai_governor))
        app_bot.add_handler(CommandHandler("bounty", group_econ.bounty_hunter))
        app_bot.add_handler(CommandHandler("mining", group_econ.passive_mining))

        # --- OTHER PLUGINS ---
        app_bot.add_handler(CommandHandler("global", leaderboard.global_leaderboard))
        app_bot.add_handler(CommandHandler("daily", daily.daily))
        app_bot.add_handler(CommandHandler("shop", shop.shop_menu))
        app_bot.add_handler(CommandHandler("buy", shop.buy))
        app_bot.add_handler(CallbackQueryHandler(shop.shop_callback, pattern="^shop_"))

        # --- RPG & SOCIAL ---
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob))
        app_bot.add_handler(CommandHandler("propose", social.propose))
        app_bot.add_handler(CommandHandler("marry", social.marry_status))
        app_bot.add_handler(CommandHandler("divorce", social.divorce))
        app_bot.add_handler(CallbackQueryHandler(social.proposal_callback, pattern="^marry_"))

        # --- FUN & AI ---
        app_bot.add_handler(CommandHandler("chatbot", chatbot.chatbot_menu))
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))
        app_bot.add_handler(CallbackQueryHandler(chatbot.chatbot_callback, pattern="^ai_"))

        # --- ADMIN ---
        app_bot.add_handler(CommandHandler("welcome", welcome.welcome_command))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CommandHandler("update", admin.update_bot))

        # --- MESSAGE LISTENERS (Ordered Groups) ---
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))

        # Group Listeners for XP and tracking
        app_bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, economy.check_chat_xp), group=1)
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=2)
        app_bot.add_handler(MessageHandler((filters.TEXT | filters.Sticker.ALL) & ~filters.COMMAND, chatbot.ai_message_handler), group=3)

        print("ꝛʏᴧηʙᴧᴋᴧ ʙσᴛ ꜱᴛᴀʀᴛɪɴɢ ᴩᴏʟʟɪɴɢ...")
        app_bot.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
