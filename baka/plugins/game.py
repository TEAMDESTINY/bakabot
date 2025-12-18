# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Protection Time Hidden Version

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_money, stylize_text, get_mention, is_protected
)
from baka.database import users_collection

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Reply or Tag to kill!')}", parse_mode=ParseMode.HTML)

    target_mention = get_mention(target_db)

    # Protection Check (Time hidden as requested)
    if is_protected(target_db):
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}", 
            parse_mode=ParseMode.HTML
        )

    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}")

    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_mention} {stylize_text('is already dead!')}", parse_mode=ParseMode.HTML)

    # Success Logic
    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker_obj.id}, {"$inc": {"kills": 1, "balance": reward}})

    await update.message.reply_text(
        f"🔪 {get_mention(attacker_obj)} {stylize_text('killed')} {target_mention}!\n"
        f"💰 <b>{stylize_text('Earned')}:</b> {format_money(reward)}", 
        parse_mode=ParseMode.HTML
    )

# --- 💰 ROB COMMAND (Full Rob + 10% Tax + Time Hidden) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sender_db = ensure_user_exists(user)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: return

    target_mention = get_mention(target_db)

    # Protection Check (Time hidden as requested)
    if is_protected(target_db):
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected by Plot Armor!')}", 
            parse_mode=ParseMode.HTML
        )

    target_bal = target_db.get('balance', 0)
    if target_bal < 100:
        return await update.message.reply_text(f"📉 {target_mention} {stylize_text('is too broke to be robbed!')}", parse_mode=ParseMode.HTML)

    if random.randint(1, 100) <= 40:
        total_stolen = target_bal
        tax = int(total_stolen * 0.10)
        final_profit = total_stolen - tax

        users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"balance": 0}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": final_profit}})
        
        msg = (
            f"💰 <b>{stylize_text('ROBBERY SUCCESS')}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>{stylize_text('Robber')}:</b> {get_mention(user)}\n"
            f"🎯 <b>{stylize_text('Victim')}:</b> {target_mention}\n\n"
            f"💸 <b>{stylize_text('Total Loot')}:</b> <code>{format_money(total_stolen)}</code>\n"
            f"⚖️ <b>{stylize_text('Market Tax (10%)')}:</b> <code>{format_money(tax)}</code>\n"
            f"✅ <b>{stylize_text('Net Profit')}:</b> <code>{format_money(final_profit)}</code>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
    else:
        fine = random.randint(200, 500)
        if sender_db.get('balance', 0) < fine: fine = sender_db.get('balance', 0)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        msg = (
            f"💀 <b>{stylize_text('ROBBERY FAILED')}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👮 {get_mention(user)} {stylize_text('pakda gaya!')}\n"
            f"🚫 <b>{stylize_text('Fine Paid')}:</b> <code>{format_money(fine)}</code>"
        )
        
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

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
