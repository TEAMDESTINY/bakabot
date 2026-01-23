# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER RYAN.PY — BAKA BOT (STABLE, SYNCED MENU)

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
)
from telegram.request import HTTPXRequest

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── INTERNAL IMPORTS ──────────────────────────────────────────────────────────
try:
    from baka.config import TOKEN, BOT_NAME
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
    print(f"CRITICAL IMPORT ERROR: {e}")
    raise SystemExit(1)

# ─── BOT COMMAND MENU (SYNCED WITH HANDLERS) ──────────────────────────────────
async def post_init(application):
    commands = [
        ("start", "sᴛᴀʀᴛ ʙᴀᴋᴀ sʏsᴛᴇᴍ 🌹"),
        ("bal", "ᴡᴀʟʟᴇᴛ ʙᴀʟᴀɴᴄᴇ 💰"),
        ("kill", "ᴋɪʟʟ sᴏᴍᴇᴏɴᴇ ⚔️"),
        ("rob", "sᴛᴇᴀʟ ᴍᴏɴᴇʏ 💸"),
        ("daily", "ᴄʟᴀɪᴍ ᴅᴀɪʟʏ ʙᴏɴᴜs 🎁"),
        ("toprich", "ʀɪᴄʜᴇsᴛ ᴘʟᴀʏᴇʀs 🏆"),
        ("brain", "ᴄʜᴇᴄᴋ ɪǫ ʟᴇᴠᴇʟ 🧠"),
        ("id", "ɢᴇᴛ ᴜsᴇʀ/ɢʀᴏᴜᴘ ɪᴅs 🆔"),
        ("ask", "ᴀsᴋ ʙᴀᴋᴀ ᴀɪ 🤖"),
        ("claim", "ᴄʟᴀɪᴍ ɢʀᴏᴜᴘ ʀᴇᴡᴀʀᴅ 💎"),
        ("sudo", "sᴜᴅᴏ ᴘᴀɴᴇʟ 🔐"),
        ("ping", "ᴄʜᴇᴄᴋ ʙᴏᴛ sᴘᴇᴇᴅ ⚡")
    ]
    await application.bot.set_my_commands(commands)
    print(f"✅ {BOT_NAME} ᴍᴇɴᴜ sʏɴᴄʜʀᴏɴɪᴢᴇᴅ!")

# ─── MAIN ENGINE ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("TOKEN missing in config")

    request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .request(request)
        .post_init(post_init)
        .build()
    )

    # ================= HANDLERS =================

    # START
    app.add_handler(CommandHandler("start", start.start))

    # ADMIN / SUDO (DIRECT ACTIONS - NO CONFIRMATION)
    app.add_handler(CommandHandler("sudo", admin.sudo_help))
    app.add_handler(CommandHandler("addcoins", admin.addcoins))
    app.add_handler(CommandHandler("rmcoins", admin.rmcoins))
    app.add_handler(CommandHandler("unprotect", admin.unprotect))
    app.add_handler(CommandHandler("freerevive", admin.freerevive))
    app.add_handler(CommandHandler("addsudo", admin.addsudo))
    app.add_handler(CommandHandler("rmsudo", admin.rmsudo))
    app.add_handler(CommandHandler("sudolist", admin.sudolist))
    app.add_handler(CommandHandler("cleandb", admin.cleandb))
    app.add_handler(CommandHandler("broadcast", broadcast.broadcast))

    # ECONOMY & GAME
    app.add_handler(CommandHandler("bal", economy.balance))
    app.add_handler(CommandHandler("daily", economy.daily_bonus))
    app.add_handler(CommandHandler("toprich", economy.toprich))
    app.add_handler(CommandHandler("myrank", economy.my_rank))
    app.add_handler(CommandHandler("topkill", economy.top_kill))
    app.add_handler(CommandHandler("give", economy.give))
    app.add_handler(CommandHandler("kill", game.kill))
    app.add_handler(CommandHandler("rob", game.rob))
    app.add_handler(CommandHandler("revive", game.revive))
    app.add_handler(CommandHandler("protect", game.protect))

    # FUN, GAMBLING & AI
    app.add_handler(CommandHandler("brain", fun.brain))
    app.add_handler(CommandHandler("id", fun.get_id))
    app.add_handler(CommandHandler("dice", fun.dice))
    app.add_handler(CommandHandler("slots", fun.slots))
    app.add_handler(CommandHandler("slap", fun.slap))
    app.add_handler(CommandHandler("punch", fun.punch))
    app.add_handler(CommandHandler("hug", fun.hug))
    app.add_handler(CommandHandler("kiss", fun.kiss))
    app.add_handler(CommandHandler("roast", fun.roast))
    app.add_handler(CommandHandler("shayari", fun.shayari))
    app.add_handler(CommandHandler("pat", fun.anime_react))
    app.add_handler(CommandHandler("bite", fun.anime_react))
    app.add_handler(CommandHandler("ask", chatbot.ask_ai))

    # SYSTEM / EVENTS
    app.add_handler(CommandHandler("ping", ping.ping))
    app.add_handler(CommandHandler("open", events.open_economy))
    app.add_handler(CommandHandler("close", events.close_economy))
    app.add_handler(CommandHandler("claim", events.claim_group))

    # MESSAGE HANDLERS (AI & STICKERS)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot.ai_message_handler))
    app.add_handler(MessageHandler(filters.Sticker.ALL, chatbot.ai_message_handler))

    # GROUP TRACKERS & WELCOME
    app.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)
    app.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))

    print(f"🚀 {BOT_NAME} ᴍᴀsᴛᴇʀ ᴇɴɢɪɴᴇ ᴏɴʟɪɴᴇ (ᴠᴘs ᴍᴏᴅᴇ)")
    app.run_polling(drop_pending_updates=True)
