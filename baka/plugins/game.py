# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game/RPG Plugin - Dual Protection (Rob & Kill) with Clean UI

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_time, format_money, stylize_text
)
from baka.database import users_collection

# --- Helper: Clickable Name with Bold Italic Serif (ID Hidden) ---
def get_clean_mention(user_id, name):
    return f"<a href='tg://user?id={user_id}'><b><i>{name}</i></b></a>"

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Reply or Tag to kill!')}", parse_mode=ParseMode.HTML)

    attacker_mention = get_clean_mention(attacker_obj.id, attacker_obj.first_name)
    target_user = target_db.get('user_obj')
    t_name = target_user.first_name if hasattr(target_user, 'first_name') else "User"
    target_mention = get_clean_mention(target_db['user_id'], t_name)

    if target_db.get('user_id') == OWNER_ID: 
        return await update.message.reply_text(f"🙊 <b>{stylize_text('Senpai Shield!')}</b>", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}", parse_mode=ParseMode.HTML)

    # --- 🛡️ PROTECTION CHECK (KILLS) ---
    expiry = get_active_protection(target_db)
    if expiry:
        # Matches Image_d93859.png
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}", 
            parse_mode=ParseMode.HTML
        )

    reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"kills": 1, "balance": reward}})

    # Matches Image_cecb89.png
    kill_msg = (
        f"👤 {attacker_mention} killed {target_mention}<b>!</b>\n"
        f"💰 <b>Earned:</b> {format_money(reward)}"
    )
    await update.message.reply_text(kill_msg, parse_mode=ParseMode.HTML)

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    if not context.args: return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: <code>/rob 100</code>", parse_mode=ParseMode.HTML)
    try: amount = int(context.args[0])
    except: return await update.message.reply_text(f"❌ {stylize_text('Sahi raqam likho!')}")

    target_db, error = await resolve_target(update, context, specific_arg=context.args[1] if len(context.args) > 1 else None)
    if not target_db: return await update.message.reply_text(f"⚠️ {stylize_text('Victim missing!')}", parse_mode=ParseMode.HTML)

    attacker_mention = get_clean_mention(attacker_obj.id, attacker_obj.first_name)
    target_user = target_db.get('user_obj')
    t_name = target_user.first_name if hasattr(target_user, 'first_name') else "User"
    target_mention = get_clean_mention(target_db['user_id'], t_name)

    # --- 🛡️ PROTECTION CHECK (ROBBERY) ---
    expiry = get_active_protection(target_db)
    if expiry:
        # Matches Image_d93859.png format
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}", 
            parse_mode=ParseMode.HTML
        )

    if target_db.get('balance', 0) < amount: 
        # Matches Image_ccf68a.png (Fixed ParseMode)
        return await update.message.reply_text(
            f"📉 {target_mention} {stylize_text('ke paas itne paise nahi hain.')}", 
            parse_mode=ParseMode.HTML
        )

    users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"balance": amount}})
    
    # Matches Image_caa571.png & Image_ccf6cc.png
    rob_msg = f"👤 {attacker_mention} robbed <b>{format_money(amount)}</b> from {target_mention} <b>!</b>"
    await update.message.reply_text(rob_msg, parse_mode=ParseMode.HTML)

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('status') == 'alive': return await update.message.reply_text(f"✨ {stylize_text('Already Alive')}")
    
    users_collection.update_one({"user_id": user.id}, {"$set": {"status": "alive"}, "$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)
