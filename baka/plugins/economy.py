# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Clean HTML (No Tap-to-Copy)

import html
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.config import DAILY_BONUS, REVIVE_COST
from baka.utils import ensure_user_exists, format_money, resolve_target
from baka.database import users_collection, groups_collection

async def check_economy(update: Update):
    if update.effective_chat.type == ChatType.PRIVATE: return True
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("<b>⚠️ Economy is disabled. Use /open to enable.</b>", parse_mode=ParseMode.HTML)
        return False
    return True

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    target_db, _ = await resolve_target(update, context)
    if not target_db: target_db = ensure_user_exists(update.effective_user)
    
    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    
    msg = (
        f"👤 <b>Name:</b> {html.escape(target_db.get('name', 'User'))}\n"
        f"💰 <b>Balance:</b> {format_money(bal)}\n"
        f"🏆 <b>Global Rank:</b> {rank}\n"
        f"❤️ <b>Status:</b> {target_db.get('status', 'alive')}\n"
        f"⚔️ <b>Kills:</b> {target_db.get('kills', 0)}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def my_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user_db = ensure_user_exists(update.effective_user)
    rank = users_collection.count_documents({"balance": {"$gt": user_db.get("balance", 0)}}) + 1
    await update.message.reply_text(f"🏆 <b>Global Rank:</b> {rank}", parse_mode=ParseMode.HTML)

async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    msg = "🏆 <b>GLOBAL TOP 10 RICHEST</b>\n\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"<b>{i}.</b> {html.escape(user.get('name', 'User'))} » {format_money(user.get('balance', 0))}\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def top_kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    killers = users_collection.find().sort("kills", -1).limit(10)
    msg = "☠️ <b>GLOBAL TOP 10 KILLERS</b>\n\n"
    for i, user in enumerate(killers, 1):
        msg += f"<b>{i}.</b> {html.escape(user.get('name', 'User'))} » {user.get('kills', 0)} kills\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if update.effective_chat.type != ChatType.PRIVATE:
        return await update.message.reply_text("<b>❌ Daily bonus is DM only!</b>", parse_mode=ParseMode.HTML)
    users_collection.update_one({"user_id": update.effective_user.id}, {"$inc": {"balance": DAILY_BONUS}, "$set": {"last_daily_claim": datetime.utcnow()}})
    await update.message.reply_text(f"<b>✅ You received: ${DAILY_BONUS} daily reward!</b>", parse_mode=ParseMode.HTML)

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("<b>Usage: Reply with /give &lt;amount&gt;</b>", parse_mode=ParseMode.HTML)
    try:
        amount = int(context.args[0])
        sender = ensure_user_exists(update.effective_user)
        receiver = ensure_user_exists(update.message.reply_to_message.from_user)
        if sender["balance"] < amount: return await update.message.reply_text("<b>❌ Insufficient balance.</b>", parse_mode=ParseMode.HTML)
        users_collection.update_one({"user_id": sender["user_id"]}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": receiver["user_id"]}, {"$inc": {"balance": amount}})
        await update.message.reply_text(f"<b>🎁 Success! Sent {format_money(amount)} to {receiver['name']}.</b>", parse_mode=ParseMode.HTML)
    except: await update.message.reply_text("<b>❌ Invalid amount.</b>", parse_mode=ParseMode.HTML)
