# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Destiny / Baka Bot 
# Fixed: "User" name issue | Double DM Alerts | Tax Rob

import random
import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_money, stylize_text, get_mention, is_protected,
    is_user_new, notify_victim
)
from baka.database import users_collection

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    
    if is_user_new(attacker.id):
        return await update.message.reply_text(
            f"❌ <b>{stylize_text('Action Denied')}!</b>\n\n👋 {get_mention(attacker)}, pehle bot start karo!",
            parse_mode=ParseMode.HTML
        )

    attacker_db = ensure_user_exists(attacker)
    target_db, error = await resolve_target(update, context)
    
    if not target_db:
        return await update.message.reply_text(f"❌ <b>{stylize_text('Target Invalid')}!</b>\n\nSaamne wale ne bot start nahi kiya!")

    # --- ⚡ REAL-TIME NAME FIX ---
    # Database ke 'User' name ko bypass karke direct Telegram se naam uthana
    target_obj = None
    if update.message.reply_to_message:
        target_obj = update.message.reply_to_message.from_user
    
    t_name = target_obj.first_name if target_obj else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"
    # --------------------------

    if is_protected(target_db):
        return await update.message.reply_text(f"🛡️ {target_mention} {stylize_text('is protected right now!')}", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}")
    
    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_mention} {stylize_text('is already dead!')}", parse_mode=ParseMode.HTML)

    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"kills": 1, "balance": reward}})

    await update.message.reply_text(
        f"🔪 {get_mention(attacker)} {stylize_text('killed')} {target_mention}!\n💰 <b>{stylize_text('Earned')}:</b> {format_money(reward)}", 
        parse_mode=ParseMode.HTML
    )

    # 📩 DOUBLE DM NOTIFICATION
    v_alert = (f"☠️ <b>{stylize_text('YOU WERE KILLED')}!</b>\n\n👤 <b>{stylize_text('Killer')}:</b> {get_mention(attacker)}\n"
               f"🏰 <b>{stylize_text('Chat')}:</b> {update.effective_chat.title}")
    a_alert = (f"🩸 <b>{stylize_text('KILL SUCCESS')}!</b>\n\n🎯 <b>{stylize_text('Victim')}:</b> {target_mention}\n"
               f"💰 <b>{stylize_text('Loot')}:</b> {format_money(reward)}")
    
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

    # --- ⚡ REAL-TIME NAME FIX ---
    target_obj = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    t_name = target_obj.first_name if target_obj else target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(t_name)}</b></a>"
    # --------------------------

    if is_protected(target_db):
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

        v_alert = (f"💸 <b>{stylize_text('YOU WERE ROBBED')}!</b>\n\n👤 <b>{stylize_text('Robber')}:</b> {get_mention(user)}\n"
                   f"💰 <b>{stylize_text('Loss')}:</b> {format_money(total_stolen)}")
        a_alert = (f"🏦 <b>{stylize_text('ROBBERY SUCCESS')}!</b>\n\n🎯 <b>{stylize_text('Target')}:</b> {target_mention}\n"
                   f"💵 <b>{stylize_text('Stolen')}:</b> {format_money(total_stolen)}")
        
        await notify_victim(context.bot, target_db['user_id'], v_alert)
        await notify_victim(context.bot, user.id, a_alert)
    else:
        fine = random.randint(200, 500)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(f"💀 {stylize_text('Robbery failed! Fine')}: {format_money(fine)}")

# --- 🛡️ PROTECT & ❤️ REVIVE (Keep as is) ---
async def protect(update, context):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST:
        return await update.message.reply_text(f"❌ {stylize_text('No money for Shield!')}")
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>{stylize_text('SHIELD ACTIVATED')}!</b>", parse_mode=ParseMode.HTML)

async def revive(update, context):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('status') == 'alive': return await update.message.reply_text(f"✨ Already alive!")
    if user_db.get('balance', 0) < REVIVE_COST: return await update.message.reply_text(f"❌ No money!")
    users_collection.update_one({"user_id": user.id}, {"$set": {"status": "alive", "death_time": None}, "$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)
