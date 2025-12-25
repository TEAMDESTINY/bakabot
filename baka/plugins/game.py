# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Custom Amount Robbing & Absolute Protection

import random
import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, format_money, 
    stylize_text, get_mention, is_protected, notify_victim
)
from baka.database import users_collection

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)

    # Target resolve logic
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db = ensure_user_exists(target_user) if target_user else (await resolve_target(update, context))[0]
    
    if not target_db: return await update.message.reply_text("❌ User nahi mila!")

    t_name = target_user.first_name if target_user else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"

    # 🔥 🛡️ Protection Check
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ This <b>{html.escape(t_name)}</b> is protected.", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 Pehle khud revive ho jao!")
    
    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_mention} is already dead!", parse_mode=ParseMode.HTML)

    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward, "kills": 1}})

    msg = (
        f"🔪 <b>{stylize_text('MURDERED')}!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Killer:</b> {get_mention(attacker)}\n"
        f"☠️ <b>Victim:</b> {target_mention}\n"
        f"💰 <b>Reward:</b> <code>{format_money(reward)}</code>\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    await notify_victim(context.bot, target_db['user_id'], f"☠️ <b>Killed by</b> {get_mention(attacker)}")

# --- 💰 ROB COMMAND (FIXED FOR CUSTOM AMOUNT) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Loot the exact amount specified in command args."""
    user = update.effective_user
    ensure_user_exists(user)

    # Must be a reply to rob
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ <b>Usage:</b> Reply to someone with <code>/rob [amount]</code>")

    target_user = update.message.reply_to_message.from_user
    target_db = ensure_user_exists(target_user)

    if target_user.id == user.id:
        return await update.message.reply_text("🙄 Apne aap ko kaise lootoge?")

    # Parse custom amount
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("⚠️ Please specify amount! Example: <code>/rob 3282</code>")
    
    rob_amount = int(context.args[0])
    target_bal = target_db.get('balance', 0)

    # 🔥 🛡️ Protection Check
    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ Target is protected!")

    # Check if victim has enough balance
    if target_bal < rob_amount:
        return await update.message.reply_text(f"📉 Target ke paas sirf {format_money(target_bal)} hai!")

    # Perform Loot
    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount}})

    await update.message.reply_text(
        f"💰 <b>Success!</b> Looted <code>{format_money(rob_amount)}</code> from {get_mention(target_user)}!",
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('status') == 'alive': 
        return await update.message.reply_text("✨ You are already alive!")
    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"❌ Revive cost: {format_money(REVIVE_COST)}")
    
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"status": "alive", "death_time": None}, "$inc": {"balance": -REVIVE_COST}}
    )
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST: 
        return await update.message.reply_text("❌ Low balance!")
    
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}}
    )
    await update.message.reply_text(f"🛡️ <b>Shield Activated!</b> Safe for 24 hours.", parse_mode=ParseMode.HTML)
