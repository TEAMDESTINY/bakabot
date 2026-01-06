# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Matches Screenshots Exactly

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

# --- 🛠️ HELPER: ECONOMY STATUS CHECK (As per Screenshots) ---
async def check_economy(update: Update):
    """Checks if economy is enabled. Sends alert if disabled."""
    if update.effective_chat.type == "private":
        return True
    
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        # Exact alert as per image_19a690.png
        await update.message.reply_text(
            "⚠️ For reopen use: /open"
        )
        return False
    return True

# --- ⚔️ ROB COMMAND (As per image_19a3cd.png) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attempts to rob a user."""
    if not await check_economy(update): return

    # Usage alert if no reply or amount
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text(
            "❗ Usage: Reply with <code>/rob <amount></code>",
            parse_mode=ParseMode.HTML
        )
    
    # ... baki rob ka logic yahan aayega ...

# --- 💰 BALANCE COMMAND ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    
    target_db, error = await resolve_target(update, context)
    if not target_db: target_db = ensure_user_exists(update.effective_user)
    
    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    
    msg = (
        f"👤 <b>Name:</b> {html.escape(target_db.get('name', 'User'))}\n"
        f"💰 <b>Total Balance:</b> <code>{format_money(bal)}</code>\n"
        f"🏆 <b>Global Rank:</b> {rank}\n"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🌍 TOP RICH COMMAND ---
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    msg = f"🏆 <b>{stylize_text('GLOBAL TOP 10 RICHEST')}</b>\n━━━━━━━━━━━━━━━━━━\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"<b>{i}.</b> {html.escape(user.get('name', 'User'))} » <code>{format_money(user.get('balance', 0))}</code>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🎁 GIVE COMMAND ---
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    
    sender = ensure_user_exists(update.effective_user)
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ Usage: Reply with /give <amount>")

    # ... baki give ka logic ...

# --- 📅 DAILY BONUS COMMAND ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    
    user = update.effective_user
    user_db = ensure_user_exists(user)
    last_claim = user_db.get("last_daily_claim")
    now = datetime.utcnow()
    
    if last_claim and (now - last_claim < timedelta(hours=24)):
        wait = timedelta(hours=24) - (now - last_claim)
        return await update.message.reply_text(f"⏳ Come back in {wait.seconds // 3600}h {(wait.seconds // 60) % 60}m.")

    REWARD = 1000
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": REWARD}, "$set": {"last_daily_claim": now}})
    
    # Exact text from Screenshot
    await update.message.reply_text(
        f"✅ You received: ${REWARD} daily reward!\n"
        f"💗 Upgrade to premium using /pay to get $2000 daily reward!"
    )
