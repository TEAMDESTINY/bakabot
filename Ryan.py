import logging
from pytz import UTC

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
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
    from baka.config import TOKEN
    from baka.utils import BOT_NAME

    import baka.plugins.start as start
    import baka.plugins.economy as economy
    import baka.plugins.game as game
    import baka.plugins.admin as admin
    import baka.plugins.broadcast as broadcast
    import baka.plugins.fun as fun
    import baka.plugins.events as events
    import baka.plugins.ping as ping
    import baka.plugins.welcome as welcome

except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    raise SystemExit(1)

# --- BOT COMMAND MENU ---
async def post_init(application):
    commands = [
        ("start", "Start the bot"),
        ("welcome", "Welcome message setup"),

        ("sudo", "Sudo control panel"),
        ("addcoins", "Add coins to user"),
        ("rmcoins", "Remove coins from user"),
        ("unprotect", "Remove protection"),
        ("freerevive", "Free revive user"),
        ("addsudo", "Add sudo user"),
        ("rmsudo", "Remove sudo user"),
        ("sudolist", "List sudo users"),
        ("cleandb", "Clean database"),
        ("broadcast", "Broadcast message"),

        ("bal", "Check wallet balance"),
        ("daily", "Daily bonus"),
        ("toprich", "Top richest users"),
        ("myrank", "Your rank"),
        ("topkill", "Top killers"),
        ("give", "Give coins to user"),

        ("kill", "Kill a user"),
        ("rob", "Rob a user"),
        ("revive", "Revive yourself"),
        ("protect", "Enable protection"),

        ("brain", "Check IQ level"),
        ("id", "Get user/chat ID"),
        ("dice", "Roll dice"),
        ("slots", "Slot machine"),
        ("slap", "Slap someone"),
        ("punch", "Punch someone"),
        ("hug", "Hug someone"),
        ("kiss", "Kiss someone"),

        ("ping", "Check bot ping"),
        ("open", "Open economy"),
        ("close", "Close economy"),
    ]

    await application.bot.set_my_commands(commands)

# --- MAIN ---
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("BOT TOKEN IS MISSING")

    request = HTTPXRequest(
        connection_pool_size=30,
        read_timeout=40.0,
    )

    app_bot = (
        ApplicationBuilder()
        .token(TOKEN)
        .request(request)
        .timezone(UTC)          # ✅ FIX FOR APSCHEDULER ERROR
        .post_init(post_init)
        .build()
    )

    # Core & Welcome
    app_bot.add_handler(CommandHandler("start", start.start))
    app_bot.add_handler(CommandHandler("welcome", welcome.welcome_command))

    # Admin
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
    app_bot.add_handler(
        CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|")
    )

    # Economy
    app_bot.add_handler(CommandHandler("bal", economy.balance))
    app_bot.add_handler(CommandHandler("daily", economy.daily_bonus))
    app_bot.add_handler(CommandHandler("toprich", economy.toprich))
    app_bot.add_handler(CommandHandler("myrank", economy.my_rank))
    app_bot.add_handler(CommandHandler("topkill", economy.top_kill))
    app_bot.add_handler(CommandHandler("give", economy.give))

    # Game
    app_bot.add_handler(CommandHandler("kill", game.kill))
    app_bot.add_handler(CommandHandler("rob", game.rob))
    app_bot.add_handler(CommandHandler("revive", game.revive))
    app_bot.add_handler(CommandHandler("protect", game.protect))

    # Fun
    app_bot.add_handler(CommandHandler("brain", fun.brain))
    app_bot.add_handler(CommandHandler("id", fun.get_id))
    app_bot.add_handler(CommandHandler("dice", fun.dice))
    app_bot.add_handler(CommandHandler("slots", fun.slots))
    app_bot.add_handler(CommandHandler("slap", fun.slap))
    app_bot.add_handler(CommandHandler("punch", fun.punch))
    app_bot.add_handler(CommandHandler("hug", fun.hug))
    app_bot.add_handler(CommandHandler("kiss", fun.kiss))

    # System
    app_bot.add_handler(CommandHandler("ping", ping.ping))
    app_bot.add_handler(CommandHandler("open", events.open_economy))
    app_bot.add_handler(CommandHandler("close", events.close_economy))

    print(f"{BOT_NAME} MASTER ENGINE ONLINE (VPS MODE)")
    app_bot.run_polling(drop_pending_updates=True)
