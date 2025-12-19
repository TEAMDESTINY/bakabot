# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Destiny / Baka Bot 
# Logic: Start Check | Inspector Logic | Double DM Alerts | Owner Bypass

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

# --- 👮 INSPECTOR APPROVAL (Owner Only) ---
async def approve_inspector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner can approve a user to check others' protection status."""
    if update.effective_user.id != OWNER_ID:
        return

    target_db, error = await resolve_target(update, context)
    if not target_db:
        return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: <code>/approve 1d @username</code>", parse_mode=ParseMode.HTML)

    # Time parsing logic (1d, 12h etc)
    time_arg = context.args[0] if context.args else "1d"
    match = re.search(r'(\d+)([dh])', time_arg.lower())
    
    if not match:
        amount, unit = 1, 'd'
    else:
        amount, unit = int(match.group(1)), match.group(2)

    expiry = datetime.utcnow() + (timedelta(days=amount) if unit == 'd' else timedelta(hours=amount))

    users_collection.update_one(
        {"user_id": target_db['user_id']},
        {"$set": {"inspector_expiry": expiry}}
    )

    await update.message.reply_text(
        f"✅ <b>{stylize_text('ACCESS GRANTED')}</b>\n"
        f"👤 {get_mention(target_db)} ab <code>{time_arg}</code> ke liye protection details dekh sakta hai!",
        parse_mode=ParseMode.HTML
    )

# --- 🔍 CHECK PROTECTION (Inspector/Owner Only) ---
async def check_protection_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approved inspectors can check protection details of any user."""
    user = update.effective_user
    user_db = ensure_user_exists(user)

    # Check if authorized
    if not is_inspector(user_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"❌ {stylize_text('Access Denied! Owner se approval lein.')}")

    target_db, error = await resolve_target(update, context)
    if not target_db:
        return await update.message.reply_text(f"⚠️ {stylize_text('Target specify karein!')}")

    expiry = target_db.get("protection_expiry")
    now = datetime.utcnow()

    if expiry and expiry > now:
        rem_time = format_time(expiry - now)
        exp_date = expiry.strftime("%d-%m-%Y %I:%M %p")
        msg = (
            f"🛡️ <b>{stylize_text('PROTECTION DATA')}</b>\n\n"
            f"👤 <b>Target:</b> {get_mention(target_db)}\n"
            f"⏳ <b>Time Left:</b> <code>{rem_time}</code>\n"
            f"📅 <b>Expiry:</b> <code>{exp_date}</code>"
        )
    else:
        msg = f"❌ {get_mention(target_db)} {stylize_text('ke paas koi active shield nahi hai.')}"

    try:
        await context.bot.send_message(chat_id=user.id, text=msg, parse_mode=ParseMode.HTML)
        await update.message.reply_text(f"📩 {stylize_text('Details DM mein bhej di gayi hain!')}")
    except:
        await update.message.reply_text(f"❌ {stylize_text('Pehle bot start karo taaki main DM bhej sakun!')}")

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    if is_user_new(attacker.id):
        return await update.message.reply_text(f"❌ <b>{stylize_text('Action Denied')}!</b>\n\n👋 {get_mention(attacker)}, pehle bot start karo!", parse_mode=ParseMode.HTML)

    attacker_db = ensure_user_exists(attacker)
    target_db, error = await resolve_target(update, context)
    if not target_db:
        return await update.message.reply_text(f"❌ <b>{stylize_text('Target Invalid')}!</b>\n\nSaamne wale ne bot start nahi kiya!")

    # Real-time name sync
    target_obj = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    t_name = target_obj.first_name if target_obj else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"

    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {target_mention} {stylize_text('is protected right now!')}", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}")
    
    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_mention} {stylize_text('is already dead!')}", parse_mode=ParseMode.HTML)

    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"kills": 1, "balance": reward}})

    await update.message.reply_text(f"🔪 {get_mention(attacker)} {stylize_text('killed')} {target_mention}!\n💰 <b>{stylize_text('Earned')}:</b> {format_money(reward)}", parse_mode=ParseMode.HTML)

    v_alert = (f"☠️ <b>{stylize_text('YOU WERE KILLED')}!</b>\n\n👤 <b>{stylize_text('Killer')}:</b> {get_mention(attacker)}\n🏰 <b>{stylize_text('Chat')}:</b> {update.effective_chat.title}")
    a_alert = (f"🩸 <b>{stylize_text('KILL SUCCESS')}!</b>\n\n🎯 <b>{stylize_text('Victim')}:</b> {target_mention}\n💰 <b>{stylize_text('Loot')}:</b> {format_money(reward)}")
    await notify_victim(context.bot, target_db['user_id'], v_alert)
    await notify_victim(context.bot, attacker.id, a_alert)

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_user_new(user.id):
        return await update.message.reply_text(f"❌ <b>{stylize_text('Action Denied')}!</b>\n\nPehle bot start karo!")

    sender_db = ensure_user_exists(user)
    target_db, error = await resolve_target(update, context)
    if not target_db:
        return await update.message.reply_text(f"❌ {stylize_text('Victim ne bot start nahi kiya!')}")

    target_obj = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    t_name = target_obj.first_name if target_obj else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"

    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {target_mention} {stylize_text('is protected!')}", parse_mode=ParseMode.HTML)

    target_bal = target_db.get('balance', 0)
    if target_bal < 100:
        return await update.message.reply_text(f"📉 {target_mention} {stylize_text('is too broke!')}", parse_mode=ParseMode.HTML)

    if random.randint(1, 100) <= 40:
        total_stolen = target_bal
        tax = int(total_stolen * 0.10)
        final_profit = total_stolen - tax
        users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"balance": 0}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": final_profit}})
        await update.message.reply_text(f"💰 {get_mention(user)} {stylize_text('robbed')} {target_mention}!", parse_mode=ParseMode.HTML)

        v_alert = (f"💸 <b>{stylize_text('YOU WERE ROBBED')}!</b>\n\n👤 <b>{stylize_text('Robber')}:</b> {get_mention(user)}\n💰 <b>{stylize_text('Loss')}:</b> {format_money(total_stolen)}")
        a_alert = (f"🏦 <b>{stylize_text('ROBBERY SUCCESS')}!</b>\n\n🎯 <b>{stylize_text('Target')}:</b> {target_mention}\n💵 <b>{stylize_text('Stolen')}:</b> {format_money(total_stolen)}")
        await notify_victim(context.bot, target_db['user_id'], v_alert)
        await notify_victim(context.bot, user.id, a_alert)
    else:
        fine = random.randint(200, 500)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(f"💀 {stylize_text('Robbery failed! Fine paid')}: {format_money(fine)}")

# --- 🛡️ PROTECT & ❤️ REVIVE ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST: return await update.message.reply_text(f"❌ {stylize_text('No money for Shield!')}")
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>{stylize_text('SHIELD ACTIVATED')}!</b>", parse_mode=ParseMode.HTML)

async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('status') == 'alive': return await update.message.reply_text(f"✨ Already alive!")
    if user_db.get('balance', 0) < REVIVE_COST: return await update.message.reply_text(f"❌ No money!")
    users_collection.update_one({"user_id": user.id}, {"$set": {"status": "alive", "death_time": None}, "$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)
