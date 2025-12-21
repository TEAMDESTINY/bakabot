# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Mirror Game Plugin - Spy Intelligence | No Start Check | Dual Owner

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
    is_user_new, notify_victim, is_inspector, format_time
)
from baka.database import users_collection

# --- 👮 INSPECTOR & CLONE OWNER LOGIC ---
async def approve_inspector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Super Owner grants access to check protection status."""
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

async def check_protection_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed Target Intelligence Report."""
    user = update.effective_user
    user_db = ensure_user_exists(user)

    if not is_inspector(user_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"❌ {stylize_text('Access Denied!')}")

    target_db, error = await resolve_target(update, context)
    if not target_db: return await update.message.reply_text("⚠️ Target missing!")

    expiry = target_db.get("protection_expiry")
    now = datetime.utcnow()
    is_dead = target_db.get('status') == 'dead'
    has_shield = expiry and expiry > now

    # Intelligence Logic
    k_status = "✅ Available" if not has_shield and not is_dead else "🛡️ Blocked"
    r_status = "✅ Available" if not has_shield and target_db.get('balance', 0) >= 100 else "📉 Blocked"

    msg = (
        f"🕵️‍♂️ <b>{stylize_text('TARGET INTELLIGENCE')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Target:</b> {get_mention(target_db)}\n"
        f"❤️ <b>Status:</b> {'💀 Dead' if is_dead else '💖 Alive'}\n"
        f"🛡️ <b>Shield:</b> {format_time(expiry - now) if has_shield else 'None'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔪 <b>Kill:</b> {k_status}\n"
        f"💰 <b>Rob:</b> {r_status}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    try: await context.bot.send_message(chat_id=user.id, text=msg, parse_mode=ParseMode.HTML)
    except: await update.message.reply_text("❌ DM me bot start karo!")

# --- 🔪 KILL COMMAND (NO START CHECK) ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)

    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db = ensure_user_exists(target_user) if target_user else (await resolve_target(update, context))[0]
    
    if not target_db: return await update.message.reply_text("❌ User not found.")

    t_name = target_user.first_name if target_user else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"

    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {target_mention} is protected!", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 Pehle khud revive ho jao!")
    
    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_mention} is already dead!", parse_mode=ParseMode.HTML)

    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"kills": 1, "balance": reward}})

    await update.message.reply_text(f"🔪 {get_mention(attacker)} killed {target_mention}!\n💰 +{format_money(reward)}", parse_mode=ParseMode.HTML)
    await notify_victim(context.bot, target_db['user_id'], f"☠️ <b>Killed by</b> {get_mention(attacker)}")

# --- 💰 ROB COMMAND (FIXED) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sender_db = ensure_user_exists(user)

    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db = ensure_user_exists(target_user) if target_user else (await resolve_target(update, context))[0]

    if not target_db: return await update.message.reply_text("❌ Victim not found.")

    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ Protected!")

    target_bal = target_db.get('balance', 0)
    if target_bal < 100: return await update.message.reply_text(f"📉 Too broke!")

    if random.randint(1, 100) <= 40:
        total = target_bal
        tax = int(total * 0.10)
        users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"balance": 0}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": total - tax}})
        await update.message.reply_text(f"💰 Success! Robbed {format_money(total - tax)}", parse_mode=ParseMode.HTML)
    else:
        fine = random.randint(200, 500)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(f"💀 Failed! Fine: {format_money(fine)}")

# --- 🛡️ PROTECT & ❤️ REVIVE ---
async def protect(update, context):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST: return await update.message.reply_text("❌ Low balance!")
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>Shield Activated!</b>", parse_mode=ParseMode.HTML)

async def revive(update, context):
    user = update.effective_user
    user_db = ensure_user
