# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Normal Font & English Output

import html
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.config import DAILY_BONUS, REVIVE_COST
from baka.utils import (
    ensure_user_exists,
    format_money,
    resolve_target
)
from baka.database import users_collection, groups_collection

# --- HELPER: ECONOMY STATUS CHECK ---
async def check_economy(update: Update):
    if update.effective_chat.type == ChatType.PRIVATE:
        return True

    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("Economy is disabled. Use /open to enable.")
        return False
    return True

# --- BALANCE (Matches Screenshot 130939) ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update):
        return

    target_db, _ = await resolve_target(update, context)
    if not target_db:
        target_db = ensure_user_exists(update.effective_user)

    name = html.escape(target_db.get('name', 'User'))
    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    status = target_db.get('status', 'alive') #
    kills = target_db.get('kills', 0) #

    msg = (
        f"Name: {name}\n"
        f"Balance: {format_money(bal)}\n"
        f"Global Rank: {rank}\n"
        f"Status: {status}\n"
        f"Kills: {kills}"
    ) #
    
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- REVIVE (Cost: $500) ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('status') == 'alive':
        return await update.message.reply_text("You are already alive!")

    if user_db.get('balance', 0) < REVIVE_COST: #
        return await update.message.reply_text(f"You need {format_money(REVIVE_COST)} to revive!")

    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"status": "alive", "death_time": None}, "$inc": {"balance": -REVIVE_COST}}
    )
    
    await update.message.reply_text(f"You have been revived! Fee: {format_money(REVIVE_COST)} deducted.")

# --- ROB ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Usage: Reply with /rob <amount>")

    try:
        amount = int(context.args[0])
        if amount <= 0: return await update.message.reply_text("Amount must be positive.")
        robber = ensure_user_exists(update.effective_user)
        target = ensure_user_exists(update.message.reply_to_message.from_user)

        if robber["user_id"] == target["user_id"]:
            return await update.message.reply_text("You cannot rob yourself!")

        target_bal = target.get("balance", 0)
        if target_bal < amount: #
            return await update.message.reply_text(
                f"Target doesn't have enough money!\n"
                f"Only {format_money(target_bal)} is available in their account."
            )

        if random.choice([True, False]):
            users_collection.update_one({"user_id": target["user_id"]}, {"$inc": {"balance": -amount}})
            users_collection.update_one({"user_id": robber["user_id"]}, {"$inc": {"balance": amount}})
            await update.message.reply_text(f"Success! You robbed {format_money(amount)} from {target['name']}!")
        else:
            penalty = int(amount * 0.3)
            users_collection.update_one({"user_id": robber["user_id"]}, {"$inc": {"balance": -penalty}})
            await update.message.reply_text(f"Caught! You failed and paid a fine of {format_money(penalty)}.")
    except ValueError:
        await update.message.reply_text("Please enter a valid numeric amount.")

# --- DAILY BONUS ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if update.effective_chat.type != ChatType.PRIVATE:
        bot_username = (await context.bot.get_me()).username
        return await update.message.reply_text(
            f"Daily Bonus can only be claimed in my DM!\n\n"
            f"Click here: t.me/{bot_username} and send /daily."
        )

    user_db = ensure_user_exists(update.effective_user)
    last_claim = user_db.get("last_daily_claim")
    now = datetime.utcnow()
    if last_claim and (now - last_claim < timedelta(hours=24)):
        wait = timedelta(hours=24) - (now - last_claim)
        hours, rem = divmod(wait.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        return await update.message.reply_text(f"Come back in {hours}h {minutes}m.")

    users_collection.update_one({"user_id": update.effective_user.id}, {"$inc": {"balance": DAILY_BONUS}, "$set": {"last_daily_claim": now}})
    await update.message.reply_text(f"You received: ${DAILY_BONUS} daily reward!")

# --- TOP LISTS ---
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    msg = "GLOBAL TOP 10 RICHEST\n" + ("-" * 20) + "\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"{i}. {html.escape(user.get('name', 'User'))} » {format_money(user.get('balance', 0))}\n"
    await update.message.reply_text(msg)
