# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER RYAN.PY - BAKA BOT EDITION (STABLE)

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatMemberHandler,
    filters
)
from telegram.request import HTTPXRequest

# --- LOGGING ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- INTERNAL IMPORTS ---
try:
    from baka.config import TOKEN, BOT_NAME # BOT_NAME 'BAKA' hona chahiye config mein
    import baka.plugins.start as start
    import baka.plugins.economy as economy
    import baka.plugins.game as game
    import baka.plugins.admin as admin
    import baka.plugins.broadcast as broadcast
    import baka.plugins.fun as fun
    import baka.plugins.events as events
    import baka.plugins.ping as ping
    import baka.plugins.welcome as welcome
    import baka.plugins.chatbot as chatbot

except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    raise SystemExit(1)

# --- BOT COMMAND MENU ---
async def post_init(application):
    commands = [
        ("start", "sᴛᴀʀᴛ ʙᴀᴋᴀ sʏsᴛᴇᴍ 🌹"),
        ("bal", "ᴡᴀʟʟᴇᴛ ʙᴀʟᴀɴᴄᴇ 💰"),
        ("kill", "ᴋɪʟʟ sᴏᴍᴇᴏɴᴇ ⚔️"),
        ("rob", "sᴛᴇᴀʟ ᴍᴏɴᴇʏ 💸"),
        ("brain", "ᴄʜᴇᴄᴋ ɪǫ ʟᴇᴠᴇʟ 🧠"),
        ("id", "ɢᴇᴛ ɪᴅs 🆔"),
        ("ask", "ᴀsᴋ ʙᴀᴋᴀ ᴀɪ 🤖"),
        ("claim", "ᴄʟᴀɪᴍ ɢʀᴏᴜᴘ ʀᴇᴡᴀʀᴅ 🎁"),
        ("sudo", "sᴜᴅᴏ ᴘᴀɴᴇʟ 🔐")
    ]
    await application.bot.set_my_commands(commands)
    print(f"✅ {BOT_NAME} ᴍᴇɴᴜ sʏɴᴄʜʀᴏɴɪᴢᴇᴅ!")

# --- MAIN ENGINE ---
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("TOKEN is missing in environment variables")

    request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)

    app_bot = (
        ApplicationBuilder()
        .token(TOKEN)
        .request(request)
        .post_init(post_init)
        .build()
    )

    # --- HANDLERS REGISTRATION ---

    # 1. Admin & Sudo (Inhe upar rakha hai taaki preference mile)
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

    # 2. Economy & Games
    app_bot.add_handler(CommandHandler("bal", economy.balance))
    app_bot.add_handler(CommandHandler("daily", economy.daily_bonus))
    app_bot.add_handler(CommandHandler("toprich", economy.toprich))
    app_bot.add_handler(CommandHandler("myrank", economy.my_rank))
    app_bot.add_handler(CommandHandler("topkill", economy.top_kill))
    app_bot.add_handler(CommandHandler("give", economy.give))
    app_bot.add_handler(CommandHandler("kill", game.kill))
    app_bot.add_handler(CommandHandler("rob", game.rob))
    app_bot.add_handler(CommandHandler("revive", game.revive))
    app_bot.add_handler(CommandHandler("protect", game.protect))

    # 3. Fun & AI
    app_bot.add_handler(CommandHandler("brain", fun.brain))
    app_bot.add_handler(CommandHandler("id", fun.get_id))
    app_bot.add_handler(CommandHandler("dice", fun.dice))
    app_bot.add_handler(CommandHandler("slots", fun.slots))
    app_bot.add_handler(CommandHandler("slap", fun.slap))
    app_bot.add_handler(CommandHandler("punch", fun.punch))
    app_bot.add_handler(CommandHandler("hug", fun.hug))
    app_bot.add_handler(CommandHandler("kiss", fun.kiss))
    app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))
    
    # 4. System & Chatbot (Filters updated for group/private accuracy)
    app_bot.add_handler(CommandHandler("ping", ping.ping))
    app_bot.add_handler(CommandHandler("open", events.open_economy))
    app_bot.add_handler(CommandHandler("close", events.close_economy))
    app_bot.add_handler(CommandHandler("claim", events.claim_group))
    
    # MessageHandlers (Text aur Stickers ke liye)
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chatbot.ai_message_handler))
    app_bot.add_handler(MessageHandler(filters.Sticker.ALL, chatbot.ai_message_handler))

    # Trackers
    app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)
    app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
    app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))
    app_bot.add_handler(CommandHandler("start", start.start))

    print(f"🚀 {BOT_NAME} ᴍᴀsᴛᴇʀ ᴇɴɢɪɴᴇ ᴏɴʟɪɴᴇ!")
    app_bot.run_polling(drop_pending_updates=True)
