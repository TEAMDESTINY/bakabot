# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game/RPG Plugin - Dual Protection (Rob & Kill) Fully Integrated

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
from baka.plugins.chatbot import ask_mistral_raw

# --- AI NARRATION ---
async def get_narrative(action_type, attacker_mention, target_mention):
    prompt = f"Write a funny, savage {action_type} message where 'P1' interacts with 'P2'. Max 15 words. Use Hinglish."
    res = await ask_mistral_raw("Game Narrator", prompt, 50)
    text = res if res and "P1" in res else f"P1 {action_type} P2!"
    return text.replace("P1", attacker_mention).replace("P2", target_mention)

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        return await update.message.reply_text(error or f"⚠️ {stylize_text('Reply or Tag to kill!')}", parse_mode=ParseMode.HTML)

    # Clean Mentions logic
    attacker_mention = f"<a href='tg://user?id={attacker_obj.id}'><b><i>{attacker_obj.first_name}</i></b></a>"
    target_user = target_db.get('user_obj')
    t_name = target_user.first_name if hasattr(target_user, 'first_name') else "User"
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b><i>{t_name}</i></b></a>"

    if target_db.get('user_id') == OWNER_ID: 
        return await update.message.reply_text(f"🙊 <b>{stylize_text('Senpai Shield!')}</b> Owner ko nahi maar sakte.", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 <b>{stylize_text('Pehle khud revive ho jao!')}</b> Aap mare hue hain.", parse_mode=ParseMode.HTML)
    
    if target_db.get('status') == 'dead': 
        return await update.message.reply_text(f"⚰️ <b>{stylize_text('Murdon ko dubara nahi maarte!')}</b>", parse_mode=ParseMode.HTML)

    # --- 🛡️ PROTECTION CHECK (Murder) ---
    expiry = get_active_protection(target_db)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(
            f"🛡️ <b>{stylize_text('BLOCKED')}!</b>\n\n"
            f"{target_mention} {stylize_text('is under protection for')} <code>{format_time(rem)}</code>.",
            parse_mode=ParseMode.HTML
        )

    base_reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"kills": 1, "balance": base_reward}})

    narration = await get_narrative("kill", attacker_mention, target_mention)
    await update.message.reply_text(
        f"🔪 <b>{stylize_text('MURDER')}!</b>\n\n📝 <i>{narration}</i>\n\n"
        f"😈 <b>Killer:</b> {attacker_mention}\n💀 <b>Victim:</b> {target_mention}\n"
        f"💵 <b>Loot:</b> <code>{format_money(base_reward)}</code>", parse_mode=ParseMode.HTML
    )

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    if not context.args: return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: <code>/rob 100 @user</code>", parse_mode=ParseMode.HTML)
    try: amount = int(context.args[0])
    except: return await update.message.reply_text(f"⚠️ {stylize_text('Sahi raqam likho!')}", parse_mode=ParseMode.HTML)

    target_db, error = await resolve_target(update, context, specific_arg=context.args[1] if len(context.args) > 1 else None)
    if not target_db: return await update.message.reply_text(error or f"⚠️ {stylize_text('Victim missing!')}", parse_mode=ParseMode.HTML)

    # Clean Mentions logic
    attacker_mention = f"<a href='tg://user?id={attacker_obj.id}'><b><i>{attacker_obj.first_name}</i></b></a>"
    target_user = target_db.get('user_obj')
    t_name = target_user.first_name if hasattr(target_user, 'first_name') else "User"
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b><i>{t_name}</i></b></a>"

    # --- 🛡️ PROTECTION CHECK (Robbery) ---
    expiry = get_active_protection(target_db)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(
            f"🛡️ <b>{stylize_text('ROBBERY FAILED')}!</b>\n\n"
            f"{target_mention} {stylize_text('has a Shield active for')} <code>{format_time(rem)}</code>.",
            parse_mode=ParseMode.HTML
        )

    if target_db.get('balance', 0) < amount: 
        return await update.message.reply_text(
            f"📉 {target_mention} {stylize_text('𝒌𝒆 𝒑𝒂𝒂𝒔 𝒊𝒕𝒏𝒆 𝒑𝒂𝒊𝒔𝒆 𝒏𝒂𝒉𝒊 𝒉𝒂𝒊𝒏.')}", 
            parse_mode=ParseMode.HTML
        )

    users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"balance": amount}})
    
    await update.message.reply_text(
        f"👤 {attacker_mention} {stylize_text('robbed')} <b>{format_money(amount)}</b> {stylize_text('from')} {target_mention} <b>!</b>",
        parse_mode=ParseMode.HTML
    )

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('balance', 0) < PROTECT_1D_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Need')} {format_money(PROTECT_1D_COST)} {stylize_text('for a Shield.')}", parse_mode=ParseMode.HTML)

    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"protection": expiry}, "$inc": {"balance": -PROTECT_1D_COST}}
    )

    await update.message.reply_text(
        f"🛡️ <b>{stylize_text('DUAL SHIELD ON')}!</b>\n\n"
        f"👤 {attacker_mention} {stylize_text('is now safe from')} <b>Murder</b> {stylize_text('and')} <b>Robbery</b> {stylize_text('for 24 hours!')}", 
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('status') == 'alive':
        return await update.message.reply_text(f"✨ {stylize_text('You are already alive!')}", parse_mode=ParseMode.HTML)

    if user_db.get('balance', 0) < REVIVE_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Need')} {format_money(REVIVE_COST)} {stylize_text('to Revive.')}", parse_mode=ParseMode.HTML)

    users_collection.update_one({"user_id": user.id}, {"$set": {"status": "alive"}, "$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(
        f"❤️ <b>{stylize_text('REVIVED')}!</b>\n\n👤 {attacker_mention} {stylize_text('is back!')}", 
        parse_mode=ParseMode.HTML
    )
