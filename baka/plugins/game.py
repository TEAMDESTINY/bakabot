# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Destiny / Baka Bot 
# Logic: Start Check | Double DM Alerts | Tax Rob | Hidden Expiry

import random
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
    
    # 🚨 1. Start Bot Check (Attacker)
    if is_user_new(attacker.id):
        return await update.message.reply_text(
            f"❌ <b>{stylize_text('Action Denied')}!</b>\n\n"
            f"👋 {get_mention(attacker)}, aapne abhi tak bot start nahi kiya hai.\n"
            f"🚀 {stylize_text('Pehle bot start karein aur daily bonus lein, fir kheliye!')}\n\n"
            f"🔗 <b>Bot Link:</b> @{context.bot.username}",
            parse_mode=ParseMode.HTML
        )

    attacker_db = ensure_user_exists(attacker)
    target_db, error = await resolve_target(update, context)
    
    # 🚨 2. Start Bot Check (Target)
    if not target_db:
        return await update.message.reply_text(
            f"❌ <b>{stylize_text('Target Invalid')}!</b>\n\n"
            f"⚠️ Saamne wale ne bot start nahi kiya hai. Use bolo pehle bot start kare tabhi aap use maar paoge!",
            parse_mode=ParseMode.HTML
        )

    target_mention = get_mention(target_db)

    # Status Checks
    if is_protected(target_db):
        return await update.message.reply_text(f"🛡️ {target_mention} {stylize_text('is protected right now!')}")
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}")
    
    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_mention} {stylize_text('is already dead!')}")

    # Success Logic
    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"kills": 1, "balance": reward}})

    # Group Message
    await update.message.reply_text(
        f"🔪 {get_mention(attacker)} {stylize_text('killed')} {target_mention}!\n"
        f"💰 <b>{stylize_text('Earned')}:</b> {format_money(reward)}", 
        parse_mode=ParseMode.HTML
    )

    # 📩 DOUBLE DM NOTIFICATION (Clickable)
    v_alert = (
        f"☠️ <b>{stylize_text('YOU WERE KILLED')}!</b>\n\n"
        f"👤 <b>{stylize_text('Killer')}:</b> {get_mention(attacker)}\n"
        f"🏰 <b>{stylize_text('Chat')}:</b> <b>{update.effective_chat.title}</b>\n\n"
        f"💉 {stylize_text('Group me /revive use karo wapas aane ke liye!')}"
    )
    a_alert = (
        f"🩸 <b>{stylize_text('KILL SUCCESS')}!</b>\n\n"
        f"🎯 <b>{stylize_text('Victim')}:</b> {target_mention}\n"
        f"💰 <b>{stylize_text('Loot')}:</b> {format_money(reward)}\n"
        f"🏰 <b>{stylize_text('Chat')}:</b> <b>{update.effective_chat.title}</b>"
    )
    
    await notify_victim(context.bot, target_db['user_id'], v_alert)
    await notify_victim(context.bot, attacker.id, a_alert)

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # 🚨 1. Start Bot Check (Robber)
    if is_user_new(user.id):
        return await update.message.reply_text(
            f"❌ <b>{stylize_text('Action Denied')}!</b>\n\n"
            f"👋 {get_mention(user)}, aapne abhi tak bot start nahi kiya hai.\n"
            f"🚀 {stylize_text('Pehle bot start karein aur daily bonus lein, fir kheliye!')}",
            parse_mode=ParseMode.HTML
        )

    sender_db = ensure_user_exists(user)
    target_db, error = await resolve_target(update, context)
    
    # 🚨 2. Start Bot Check (Target)
    if not target_db:
        return await update.message.reply_text(f"❌ {stylize_text('Victim ne bot start nahi kiya hai!')}")

    target_mention = get_mention(target_db)
    if is_protected(target_db):
        return await update.message.reply_text(f"🛡️ {target_mention} {stylize_text('is protected by Plot Armor!')}")

    target_bal = target_db.get('balance', 0)
    if target_bal < 100:
        return await update.message.reply_text(f"📉 {target_mention} {stylize_text('is too broke to be robbed!')}")

    if random.randint(1, 100) <= 40:
        # Success Logic: Full Rob + 10% Tax
        total_stolen = target_bal
        tax = int(total_stolen * 0.10)
        final_profit = total_stolen - tax

        users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"balance": 0}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": final_profit}})
        
        await update.message.reply_text(
            f"💰 {get_mention(user)} {stylize_text('successfully robbed')} {target_mention}!", 
            parse_mode=ParseMode.HTML
        )

        # 📩 DOUBLE DM NOTIFICATION (Clickable)
        v_alert = (
            f"💸 <b>{stylize_text('YOU WERE ROBBED')}!</b>\n\n"
            f"👤 <b>{stylize_text('Robber')}:</b> {get_mention(user)}\n"
            f"💰 <b>{stylize_text('Loss')}:</b> {format_money(total_stolen)}\n"
            f"🏰 <b>{stylize_text('Chat')}:</b> <b>{update.effective_chat.title}</b>"
        )
        a_alert = (
            f"🏦 <b>{stylize_text('ROBBERY SUCCESS')}!</b>\n\n"
            f"🎯 <b>{stylize_text('Target')}:</b> {target_mention}\n"
            f"💵 <b>{stylize_text('Stolen')}:</b> {format_money(total_stolen)}\n"
            f"⚖️ <b>{stylize_text('Tax')}:</b> {format_money(tax)}\n"
            f"🏰 <b>{stylize_text('Chat')}:</b> <b>{update.effective_chat.title}</b>"
        )
        
        await notify_victim(context.bot, target_db['user_id'], v_alert)
        await notify_victim(context.bot, user.id, a_alert)
    else:
        # Failure Fine
        fine = random.randint(200, 500)
        if sender_db.get('balance', 0) < fine: fine = sender_db.get('balance', 0)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(f"💀 {stylize_text('Robbery failed! Fine paid')}: {format_money(fine)}")

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('balance', 0) < PROTECT_1D_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Need')} {format_money(PROTECT_1D_COST)} {stylize_text('for Shield.')}")

    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    
    await update.message.reply_text(
        f"🛡️ <b>{stylize_text('SHIELD ACTIVATED')}!</b>\n"
        f"👤 {get_mention(user)} {stylize_text('is protected for 24h.')}", 
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('status') == 'alive':
        return await update.message.reply_text(f"✨ {stylize_text('You are already alive!')}")

    if user_db.get('balance', 0) < REVIVE_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Need')} {format_money(REVIVE_COST)} {stylize_text('to Revive.')}")

    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"status": "alive", "death_time": None}, "$inc": {"balance": -REVIVE_COST}}
    )

    await update.message.reply_text(
        f"❤️ <b>{stylize_text('REVIVED')}!</b>\n"
        f"👤 {get_mention(user)} {stylize_text('is back in the game!')}", 
        parse_mode=ParseMode.HTML
    )
