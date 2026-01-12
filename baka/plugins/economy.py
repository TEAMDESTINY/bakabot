# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Matches Screenshots Exactly & DM Daily Fixed

import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.config import TAX_RATE, DAILY_BONUS
from baka.utils import (
    ensure_user_exists, format_money, 
    resolve_target, stylize_text
)
from baka.database import users_collection, groups_collection

# --- 🛠️ HELPER: ECONOMY STATUS CHECK ---
async def check_economy(update: Update):
    """Checks if economy is enabled. Sends alert if disabled."""
    if update.effective_chat.type == ChatType.PRIVATE:
        return True
    
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("⚠️ For reopen use: /open")
        return False
    return True

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

# --- 🏆 MY RANK COMMAND ---
async def my_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user_db = ensure_user_exists(update.effective_user)
    bal = user_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    await update.message.reply_text(f"🏆 <b>Your Global Rank:</b> {rank}", parse_mode=ParseMode.HTML)

# --- 🌍 TOP RICH COMMAND ---
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    msg = f"🏆 <b>{stylize_text('GLOBAL TOP 10 RICHEST')}</b>\n━━━━━━━━━━━━━━━━━━\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"<b>{i}.</b> {html.escape(user.get('name', 'User'))} » <code>{format_money(user.get('balance', 0))}</code>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- ⚔️ TOP KILL COMMAND ---
async def top_kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    killers = users_collection.find().sort("kills", -1).limit(10)
    msg = f"⚔️ <b>{stylize_text('GLOBAL TOP 10 KILLERS')}</b>\n━━━━━━━━━━━━━━━━━━\n"
    for i, killer in enumerate(killers, 1):
        msg += f"<b>{i}.</b> {html.escape(killer.get('name', 'User'))} » <code>{killer.get('kills', 0)} Kills</code>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 📅 DAILY BONUS COMMAND (DM ONLY) ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    
    user = update.effective_user
    chat = update.effective_chat
    
    # 🛑 DM ONLY CHECK
    if chat.type != ChatType.PRIVATE:
        # Get bot username for the link
        bot_username = (await context.bot.get_me()).username
        return await update.message.reply_text(
            f"❌ <b>Daily Bonus sirf mere DM mein claim kiya ja sakta hai!</b>\n\n"
            f"👉 <a href='t.me/{bot_username}'>Yahan Click Karein</a> aur <code>/daily</code> bhejein.",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    user_db = ensure_user_exists(user)
    last_claim = user_db.get("last_daily_claim")
    now = datetime.utcnow()
    
    if last_claim and (now - last_claim < timedelta(hours=24)):
        wait = timedelta(hours=24) - (now - last_claim)
        hours, remainder = divmod(wait.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return await update.message.reply_text(f"⏳ Come back in <b>{hours}h {minutes}m</b>.", parse_mode=ParseMode.HTML)

    # Use reward from config.py
    reward = DAILY_BONUS 
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$inc": {"balance": reward}, "$set": {"last_daily_claim": now}}
    )
    
    await update.message.reply_text(
        f"✅ <b>You received: ${reward} daily reward!</b>\n"
        f"💗 Upgrade to premium using /pay to get $2000 daily reward!",
        parse_mode=ParseMode.HTML
    )

# --- 🎁 GIVE COMMAND ---
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ Usage: Reply with <code>/give &lt;amount&gt;</code>", parse_mode=ParseMode.HTML)

    try:
        amount = int(context.args[0])
        if amount <= 0: return await update.message.reply_text("❌ Amount must be positive.")
        
        sender = ensure_user_exists(update.effective_user)
        if sender['balance'] < amount:
            return await update.message.reply_text("❌ Insufficient balance.")
            
        receiver = ensure_user_exists(update.message.reply_to_message.from_user)
        
        # Transfer
        users_collection.update_one({"user_id": sender['user_id']}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": receiver['user_id']}, {"$inc": {"balance": amount}})
        
        await update.message.reply_text(f"✅ Successfully gave <b>{format_money(amount)}</b> to {receiver['name']}!")
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid amount.")
