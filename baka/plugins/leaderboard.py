# leaderboard.py
# © 2025 WTF_Phantom | XP Global Leaderboard

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from baka.database import users_collection
from baka.utils import get_user_badge

# /global — Show Global XP Leaderboard
async def global_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    top = list(users_collection.find().sort("level", -1).sort("xp", -1).limit(10))

    if not top:
        await update.message.reply_text("No users found in database.")
        return

    text = "🏆 <b>Global XP Leaderboard</b>\n"
    text += "━━━━━━━━━━━━━━━━━━\n"

    rank = 1
    for u in top:
        name = u.get("name", "User")
        level = u.get("level", 1)
        xp = u.get("xp", 0)
        badge = get_user_badge(level)

        text += f"<b>{rank}.</b> {badge} | <b>{name}</b>\n"
        text += f"  Lvl: <b>{level}</b> • XP: <code>{xp}</code>\n"
        rank += 1

    text += "━━━━━━━━━━━━━━━━━━"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
