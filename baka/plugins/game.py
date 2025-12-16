# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, PROTECT_2D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_time, format_money, get_mention, check_auto_revive, stylize_text
)
from baka.database import users_collection
from baka.plugins.chatbot import ask_mistral_raw

# --- AI NARRATION ---
async def get_narrative(action_type, attacker_mention, target_mention):
    # Narrative logic is fine
    prompt = f"Write a funny, savage {action_type} message where 'P1' interacts with 'P2'. Max 15 words. Use Hinglish."
    res = await ask_mistral_raw("Game Narrator", prompt, 50)
    text = res if res and "P1" in res else f"P1 {action_type} P2!"
    return text.replace("P1", attacker_mention).replace("P2", target_mention)

# --- KILL ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    # Resolve target: Isse database data + Telegram user object milta hai
    target_db, error = await resolve_target(update, context)
    
    if not target_db: 
        return await update.message.reply_text(error or "⚠️ <b>Reply</b> or <b>Tag</b> to kill!", parse_mode=ParseMode.HTML)

    # --- NAME FIX LOGIC ---
    # Hum seedhe update/context se Telegram names use karenge na ki sirf DB se
    attacker_mention = get_mention(attacker_obj) 
    
    # Target ka name handle karne ke liye (resolve_target se 'user_obj' field hona chahiye)
    target_user_obj = target_db.get('user_obj') or target_db
    target_mention = get_mention(target_user_obj)

    # --- SAFETY CHECKS ---
    if target_db.get('user_id') == OWNER_ID: 
        return await update.message.reply_text("🙊 <b>Senpai Shield!</b> Owner ko nahi maar sakte.", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text("💀 <b>Pehle khud revive ho jao!</b> Aap mare hue hain.", parse_mode=ParseMode.HTML)
    
    if target_db.get('status') == 'dead': 
        return await update.message.reply_text("⚰️ <b>Murdon ko dubara nahi maarte!</b>", parse_mode=ParseMode.HTML)

    expiry = get_active_protection(target_db)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(f"🛡️ <b>Blocked!</b> Protection left: <code>{format_time(rem)}</code>.", parse_mode=ParseMode.HTML)

    # --- EXECUTION ---
    base_reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"kills": 1, "balance": base_reward}})

    narration = await get_narrative("kill", attacker_mention, target_mention)

    await update.message.reply_text(
        f"🔪 <b>{stylize_text('MURDER')}!</b>\n\n"
        f"📝 <i>{narration}</i>\n\n"
        f"😈 <b>Killer:</b> {attacker_mention}\n"
        f"💀 <b>Victim:</b> {target_mention}\n"
        f"💵 <b>Loot:</b> <code>{format_money(base_reward)}</code>", 
        parse_mode=ParseMode.HTML
    )

# --- ROB ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    if not context.args: return await update.message.reply_text("⚠️ <code>/rob 100 @user</code>")
    try: amount = int(context.args[0])
    except: return await update.message.reply_text("⚠️ Invalid Amount")

    target_db, error = await resolve_target(update, context, specific_arg=context.args[1] if len(context.args) > 1 else None)
    if not target_db: return await update.message.reply_text(error or "⚠️ Victim missing.")

    # NAME FIX
    attacker_mention = get_mention(attacker_obj)
    target_user_obj = target_db.get('user_obj') or target_db
    target_mention = get_mention(target_user_obj)

    if target_db.get('balance', 0) < amount: 
        return await update.message.reply_text("📉 Target ke paas itne paise nahi hain.")

    # Execution
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"balance": amount}})
    
    narration = await get_narrative("rob", attacker_mention, target_mention)

    await update.message.reply_text(
        f"💰 <b>{stylize_text('ROBBERY')}!</b>\n\n"
        f"📝 <i>{narration}</i>\n\n"
        f"😈 <b>Thief:</b> {attacker_mention}\n"
        f"💸 <b>Stolen:</b> <code>{format_money(amount)}</code> from {target_mention}", 
        parse_mode=ParseMode.HTML
    )

# Baki Protect aur Revive logic bhi same name fix ke sath use karein.
