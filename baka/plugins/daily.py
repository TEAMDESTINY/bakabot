# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Daily Plugin - Streak System & Weekly Bonus Integrated

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, format_money, stylize_text
from baka.database import users_collection

# --- CONFIGURATION ---
DAILY_REWARD = 500
WEEKLY_BONUS = 10000

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles daily rewards and streak logic."""
    user_data = ensure_user_exists(update.effective_user)
    user_id = user_data['user_id']
    now = datetime.utcnow()
    last_claim = user_data.get("last_daily")
    
    # 1. ⏳ COOLDOWN CHECK (24 Hours)
    if last_claim and (now - last_claim) < timedelta(hours=24):
        rem = timedelta(hours=24) - (now - last_claim)
        hours = int(rem.total_seconds() // 3600)
        minutes = int((rem.total_seconds() % 3600) // 60)
        return await update.message.reply_text(
            f"⏳ <b>{stylize_text('Cooldown')}!</b>\n"
            f"Bhai, thoda sabar karo! Agla reward <b>{hours}h {minutes}m</b> baad milega.", 
            parse_mode=ParseMode.HTML
        )
    
    # 2. 🔥 STREAK LOGIC
    streak = user_data.get("daily_streak", 0)
    
    # Agar 48 ghante se zyada ho gaye, toh streak reset
    if last_claim and (now - last_claim) > timedelta(hours=48):
        streak = 0 
    
    streak += 1
    reward = DAILY_REWARD
    bonus = WEEKLY_BONUS if streak % 7 == 0 else 0
    total_reward = reward + bonus
    
    # 3. 💰 DATABASE UPDATE
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {"last_daily": now, "daily_streak": streak},
            "$inc": {"balance": total_reward}
        }
    )
    
    # 4. 📝 MESSAGE FORMATTING
    msg = (
        f"📅 <b>{stylize_text('Day')} {streak}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎁 <b>Claimed:</b> <code>{format_money(reward)}</code>\n"
    )
    
    if bonus:
        msg += f"🎉 <b>Weekly Bonus:</b> <code>{format_money(bonus)}</code>\n"
        msg += f"✨ <i>Wow! 7 din lagatar claim karne ka tohfa!</i>\n"
    
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 <b>Total Balance:</b> <code>{format_money(user_data.get('balance', 0) + total_reward)}</code>"
    
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
