# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER GAME PLUGIN - NO BYPASS & DOUBLE PROTECTION CHECK

import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from baka.config import (
    PROTECT_1D_COST, PROTECT_2D_COST, 
    REVIVE_COST, OWNER_ID
)
from baka.utils import ensure_user_exists, resolve_target, format_money
from baka.database import users_collection, groups_collection

def nezuko_style(text):
    mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
    return str(text).lower().translate(mapping)

async def check_economy(update: Update):
    if update.effective_chat.type == "private":
        return True
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("<b>⚠️ For reopen use: /open</b>", parse_mode=ParseMode.HTML)
        return False
    return True

# --- 🔪 1. KILL COMMAND (STRICT RETURN ON PROTECTION) ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    attacker = ensure_user_exists(update.effective_user)
    
    if attacker.get('status') == 'dead':
        return await update.message.reply_text(nezuko_style("❌ ʏᴏᴜ ᴀʀᴇ ᴅᴇᴀᴅ! ʀᴇᴠɪᴠᴇ ʏᴏᴜʀsᴇʟғ ғɪʀsᴛ."))

    res = await resolve_target(update, context)
    victim = res[0] if isinstance(res, (tuple, list)) else res
    if not victim:
        return await update.message.reply_text(nezuko_style("❌ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴠɪᴄᴛɪᴍ !"))

    # --- 🛡️ PROTECTION CHECK (STOP KILL) ---
    now = datetime.utcnow()
    expiry = victim.get('protection_expiry')
    if expiry and expiry > now and update.effective_user.id != OWNER_ID:
        # RETURN lagana zaroori hai taaki niche ka kill code na chale
        return await update.message.reply_text(f"🛡️ {nezuko_style('victim is protected right now!')}")

    if victim.get('status') == 'dead':
        return await update.message.reply_text(nezuko_style(f"💀 {victim['name']} ɪs ᴀʟʀᴇᴀᴅʏ ᴅᴇᴀᴅ!"))

    reward = random.randint(100, 200)
    users_collection.update_one({"user_id": victim['user_id']}, {"$set": {"status": "dead", "death_time": now}})
    users_collection.update_one({"user_id": attacker['user_id']}, {"$inc": {"balance": reward, "kills": 1}})
    
    await update.message.reply_text(
        f"<b>👤 {attacker['name'].upper()} killed {victim['name'].upper()}!</b>\n"
        f"<b>💰 {nezuko_style('earned')}: {format_money(reward)}</b>",
        parse_mode=ParseMode.HTML
    )

# --- 💰 2. ROB COMMAND (WITH PROTECTION CHECK) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user = ensure_user_exists(update.effective_user)
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text(nezuko_style("❗ usage: reply with /rob <amount>"))

    try:
        amount = int(context.args[0])
        res = await resolve_target(update, context)
        target_db = res[0] if isinstance(res, (tuple, list)) else res

        # Rob Protection Check
        now = datetime.utcnow()
        if target_db.get('protection_expiry') and target_db['protection_expiry'] > now:
            return await update.message.reply_text(f"🛡️ {nezuko_style('victim is protected!')}")

        if target_db.get('balance', 0) < amount:
            return await update.message.reply_text(f"<b>📉 {nezuko_style('target doesnt have enough money!')}</b>", parse_mode=ParseMode.HTML)

        users_collection.update_one({"user_id": target_db['user_id']}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": user['user_id']}, {"$inc": {"balance": amount}})
        await update.message.reply_text(f"<b>💰 {user['name']} robbed {target_db['name']}!</b>\n<b>Looted: {format_money(amount)}</b>", parse_mode=ParseMode.HTML)
    except: pass

# --- ❤️ 3. REVIVE COMMAND (EXACT FORMAT) ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user = ensure_user_exists(update.effective_user)
    res = await resolve_target(update, context) if update.message.reply_to_message else user
    target_db = res[0] if isinstance(res, (tuple, list)) else res

    if target_db.get('status') == 'alive':
        user_display = f"˹ {target_db['name']} ☞♪ ᴀssɪsᴛᴀɴᴛ ˼™ 🌸"
        return await update.message.reply_text(f"✅ {user_display} is already alive!")

    if user.get('balance', 0) < REVIVE_COST:
        return await update.message.reply_text(f"<b>❌ Revive costs: {format_money(REVIVE_COST)}</b>", parse_mode=ParseMode.HTML)

    users_collection.update_one({"user_id": target_db['user_id']}, {"$set": {"status": "alive", "death_time": None}})
    users_collection.update_one({"user_id": user['user_id']}, {"$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(nezuko_style(f"💖 {target_db['name']} ʜᴀs ʙᴇᴇɴ ʀᴇᴠɪᴠᴇᴅ!"))

# --- 🛡️ 4. PROTECT COMMAND (ALREADY PROTECTED CHECK) ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user_db = ensure_user_exists(update.effective_user)
    
    # Check if already protected
    now = datetime.utcnow()
    if user_db.get('protection_expiry') and user_db['protection_expiry'] > now:
        return await update.message.reply_text(f"🛡️ {nezuko_style('you are already protected!')}")

    if not context.args:
        return await update.message.reply_text(nezuko_style("⚠️ ᴜsᴀɢᴇ: /protect 1ᴅ"))

    choice = context.args[0].lower()
    cost, days = (PROTECT_2D_COST, 2) if choice == "2d" else (PROTECT_1D_COST, 1)

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"<b>❌ You need {format_money(cost)} for protection.</b>", parse_mode=ParseMode.HTML)
    
    expiry = now + timedelta(days=days)
    users_collection.update_one({"user_id": user_db['user_id']}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -cost}})
    await update.message.reply_text(f"🛡️ {nezuko_style(f'you are now protected for {choice}.')}")
