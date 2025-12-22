# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Mirror Game Plugin - Absolute Protection Logic

import random
import html
import re
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_money, stylize_text, get_mention, is_protected,
    notify_victim, is_inspector, format_time
)
from baka.database import users_collection

# --- 👮 INSPECTOR & INTELLIGENCE ---
async def approve_inspector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    target_db, error = await resolve_target(update, context)
    if not target_db:
        return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: /approve 1d @username")
    time_arg = context.args[0] if context.args else "1d"
    match = re.search(r'(\d+)([dh])', time_arg.lower())
    amount, unit = (int(match.group(1)), match.group(2)) if match else (1, 'd')
    expiry = datetime.utcnow() + (timedelta(days=amount) if unit == 'd' else timedelta(hours=amount))
    users_collection.update_one({"user_id": target_db['user_id']}, {"$set": {"inspector_expiry": expiry}})
    await update.message.reply_text(f"✅ {get_mention(target_db)} {stylize_text('Approved')} for {time_arg}!", parse_mode=ParseMode.HTML)

# --- 🔪 KILL COMMAND (FIXED PROTECTION) ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)

    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db = ensure_user_exists(target_user) if target_user else (await resolve_target(update, context))[0]
    
    if not target_db: return await update.message.reply_text("❌ User nahi mila!")

    t_name = target_user.first_name if target_user else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"

    # 🔥 🛡️ ABSOLUTE KILL PROTECTION
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ 𝖥 {t_name} is protected. Kill attempt failed!", parse_mode=ParseMode.HTML)
    
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

# --- 💰 ROB COMMAND (FIXED PROTECTION) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sender_db = ensure_user_exists(user)

    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db, err = await resolve_target(update, context) if not target_user else (ensure_user_exists(target_user), None)

    if not target_db: return await update.message.reply_text("❌ Victim nahi mila!")

    t_name = target_user.first_name if target_user else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"

    # 🔥 🛡️ ABSOLUTE ROB PROTECTION
    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ 𝖥 {t_name} is protected. Robbery failed!", parse_mode=ParseMode.HTML)

    target_bal = target_db.get('balance', 0)
    if target_bal < 100: return await update.message.reply_text(f"📉 {t_name} bahut gareeb hai!")

    if random.randint(1, 100) <= 40:
        loot_percent = random.randint(30, 70)
        loot_amount = int(target_bal * (loot_percent / 100))
        users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -loot_amount}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot_amount}})
        await update.message.reply_text(f"💰 <b>Success!</b> Looted <b>{format_money(loot_amount)}</b> from {target_mention}", parse_mode=ParseMode.HTML)
    else:
        fine = random.randint(200, 500)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(f"💀 <b>Failed!</b>\nAap pakde gaye aur <b>{format_money(fine)}</b> jurmana bharna pada.", parse_mode=ParseMode.HTML)

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
async def protect(update, context):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST: return await update.message.reply_text("❌ Low balance!")
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>Shield Activated!</b>", parse_mode=ParseMode.HTML)
