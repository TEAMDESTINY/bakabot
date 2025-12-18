# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game/RPG Plugin - Exact Baka Bot Replica UI

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_money, stylize_text
)
from baka.database import users_collection

# --- Helper: Baka Style Clickable Name (No ID, Bold Italic) ---
def get_baka_mention(user_id, name):
    # Sirf Stylish Name clickable hoga, screen par ID nahi aayegi
    return f"<a href='tg://user?id={user_id}'><b><i>{name}</i></b></a>"

# --- 🔪 KILL COMMAND (Image_cecb89 Replica) ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Reply or Tag to kill!')}", parse_mode=ParseMode.HTML)

    attacker_mention = get_baka_mention(attacker_obj.id, attacker_obj.first_name)
    target_user = target_db.get('user_obj')
    t_name = target_user.first_name if hasattr(target_user, 'first_name') else "User"
    target_mention = get_baka_mention(target_db['user_id'], t_name)

    # Status Checks
    if target_db.get('user_id') == OWNER_ID: 
        return await update.message.reply_text(f"🙊 <b>{stylize_text('Senpai Shield!')}</b>", parse_mode=ParseMode.HTML)
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}", parse_mode=ParseMode.HTML)
    if target_db.get('status') == 'dead': 
        return await update.message.reply_text(f"⚰️ {stylize_text('Murdon ko dubara nahi maarte!')}", parse_mode=ParseMode.HTML)

    # --- Protection Block (Image_d93859 Replica) ---
    if get_active_protection(target_db):
        return await update.message.reply_text(
            f"🛡️ {target_mention} is protected right now!", 
            parse_mode=ParseMode.HTML
        )

    # Execution
    reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"kills": 1, "balance": reward}})

    # EXACT Layout like Screenshot
    await update.message.reply_text(
        f"👤 {attacker_mention} killed {target_mention}!\n"
        f"💰 Earned: {format_money(reward)}", 
        parse_mode=ParseMode.HTML
    )

# --- 💰 ROB COMMAND (Image_caa571 & Image_ccf6cc Replica) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    if not context.args: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: <code>/rob 100</code>", parse_mode=ParseMode.HTML)
    
    try: amount = int(context.args[0])
    except: return

    target_db, error = await resolve_target(update, context, specific_arg=context.args[1] if len(context.args) > 1 else None)
    if not target_db: return

    attacker_mention = get_baka_mention(attacker_obj.id, attacker_obj.first_name)
    target_user = target_db.get('user_obj')
    t_name = target_user.first_name if hasattr(target_user, 'first_name') else "User"
    target_mention = get_baka_mention(target_db['user_id'], t_name)

    # --- Protection Block (Image_d93859 / Image_d9b12f Replica) ---
    if get_active_protection(target_db):
        return await update.message.reply_text(
            f"🛡️ {target_mention} is protected right now!", 
            parse_mode=ParseMode.HTML
        )

    if target_db.get('balance', 0) < amount: 
        # Image_ccf68a Fix (No raw tags, clean serif)
        return await update.message.reply_text(
            f"📉 {target_mention} 𝒌𝒆 𝒑𝒂𝒂𝒔 𝒊𝒕𝒏𝒆 𝒑𝒂𝒊𝒔𝒆 𝒏𝒂𝒉𝒊 𝒉𝒂𝒊𝒏.", 
            parse_mode=ParseMode.HTML
        )

    # Execution
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"balance": amount}})
    
    # EXACT Layout like Screenshot
    await update.message.reply_text(
        f"👤 {attacker_mention} robbed <b>{format_money(amount)}</b> from {target_mention}!", 
        parse_mode=ParseMode.HTML
    )

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Low Balance')}")

    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>{stylize_text('SHIELD ON')}!</b>", parse_mode=ParseMode.HTML)

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_collection.update_one({"user_id": user.id}, {"$set": {"status": "alive"}, "$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)
