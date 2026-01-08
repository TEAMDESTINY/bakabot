# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Flash Collect Plugin - 20 Second Global Window

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.database import users_collection, events_collection
from baka.utils import format_money, ensure_user_exists, SUDO_USERS

# --- 🎁 USER COMMAND: /collect ---
async def collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows users to collect coins only during a specific 20-second window."""
    now = datetime.utcnow()
    
    # 1. Fetch the scheduled event time from the database
    event = events_collection.find_one({"event_name": "flash_collect"})
    if not event or not event.get("start_at"):
        return # Silent if no event is currently scheduled

    start_time = event["start_at"]
    end_time = start_time + timedelta(seconds=20) # 20-second window

    # 2. Check if the current time falls within the 20-second flash window
    if not (start_time <= now <= end_time):
        return # Command is inactive outside of the 20-second window

    user = update.effective_user
    user_db = ensure_user_exists(user)

    # 3. Prevention: Ensure the user only collects once per scheduled event
    if user_db.get("last_event_collected") == start_time:
        return await update.message.reply_text("🚫 You have already collected from this flash event!")

    # 4. Success: Grant a random reward between 1,000 and 3,000 coins
    reward = random.randint(1000, 3000)
    users_collection.update_one(
        {"user_id": user.id},
        {
            "$inc": {"balance": reward},
            "$set": {"last_event_collected": start_time} # Mark as collected for this specific timestamp
        }
    )

    await update.message.reply_text(
        f"🎁 <b>Flash Collect Success!</b>\n"
        f"You found <code>{format_money(reward)}</code> coins in the stash!",
        parse_mode=ParseMode.HTML
    )

# --- 👑 ADMIN COMMAND: /setflash ---
async def set_flash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets the global start time for the 20-second flash event."""
    user = update.effective_user
    
    # Check if the user is a Sudo/Admin
    if user.id not in SUDO_USERS:
        return await update.message.reply_text("❌ This is an admin-only command.")

    # Expecting format: /setflash YYYY-MM-DD HH:MM
    if len(context.args) < 2:
        return await update.message.reply_text("❗ Usage: <code>/setflash 2026-01-08 20:00</code> (UTC Time)", parse_mode=ParseMode.HTML)

    try:
        date_str = f"{context.args[0]} {context.args[1]}"
        event_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        
        # Save to database
        events_collection.update_one(
            {"event_name": "flash_collect"},
            {"$set": {"start_at": event_time}},
            upsert=True
        )
        
        await update.message.reply_text(
            f"✅ <b>Flash Event Scheduled!</b>\n"
            f"📅 Date: <code>{context.args[0]}</code>\n"
            f"⏰ Time: <code>{context.args[1]} UTC</code>\n"
            f"⌛ Duration: 20 Seconds",
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid format! Use: <code>YYYY-MM-DD HH:MM</code>")
