# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - With Toggle Check (Open/Close Support)

import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import TAX_RATE
from baka.utils import (
    ensure_user_exists, format_money, 
    resolve_target, stylize_text
)
from baka.database import users_collection, groups_collection

# --- 🛠️ HELPER: ECONOMY STATUS CHECK ---
async def check_economy(update: Update):
    """Checks if economy is enabled. Returns True if ON, False if OFF."""
    # Private chat mein hamesha ON rahegi
    if update.effective_chat.type == "private":
        return True
        
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("❌ Economy is currently disabled in this group.")
        return False
    return True

# --- 💰 BALANCE COMMAND ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return

    target_db, error = await resolve_target(update, context)
    if not target_db: 
        target_db = ensure_user_exists(update.effective_user)

    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    
    msg = (
        f"👤 <b>Name:</b> {html.escape(target_db.get('name', 'User'))}\n"
        f"💰 <b>Total Balance:</b> <code>{format_money(bal)}</code>\n"
        f"🏆 <b>Global Rank:</b> {rank}\n"
        f"❤️ <b>Status:</b> {target_db.get('status', 'alive')}\n"
        f"⚔️ <b>Kills:</b> {target_db.get('kills', 0)}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🎁 GIVE COMMAND (10% Tax) ---
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return

    sender = ensure_user_exists(update.effective_user)
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ Usage: Reply with /give <amount>")

    if not context.args[0].isdigit():
        return await update.message.reply_text("❌ Please enter a valid number!")

    amount = int(context.args[0])
    if amount <= 0: return await update.message.reply_text("❌ Amount must be positive!")

    tax = int(amount * TAX_RATE)
    total_deduction = amount + tax
    
    if sender.get('balance', 0) < total_deduction:
        return await update.message.reply_text(f"❌ You need {format_money(total_deduction)} to send this.")

    target = update.message.reply_to_message.from_user
    if target.id == sender['user_id']:
        return await update.message.reply_text("🙄 You cannot give money to yourself!")

    users_collection.update_one({"user_id": sender['user_id']}, {"$inc": {"balance": -total_deduction}})
    users_collection.update_one({"user_id": target.id}, {"$inc": {"balance": amount}})
    
    await update.message.reply_text(
        f"💸 <b>Sent:</b> <code>{format_money(amount)}</code>\nTax: {format_money(tax)}\nTo: {html.escape(target.first_name)}",
        parse_mode=ParseMode.HTML
    )

# --- 📅 DAILY BONUS COMMAND (24 HOURS) ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return

    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    last_claim = user_db.get("last_daily_claim")
    now = datetime.utcnow()
    cooldown_period = timedelta(hours=24)

    if last_claim and (now - last_claim < cooldown_period):
        remaining = cooldown_period - (now - last_claim)
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return await update.message.reply_text(f"⏳ Come back in {hours}h {minutes}m.")

    REWARD = 1000
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": REWARD}, "$set": {"last_daily_claim": now}})

    msg = (
        f"✅ You received: ${REWARD} daily reward!\n"
        f"💗 Upgrade to premium using /pay to get $2000 daily reward!"
    )
    await update.message.reply_text(msg)

# (Toprich, MyRank, aur TopKill functions mein bhi 'if not await check_economy(update): return' add kar dein)
