# FINAL MASTER GAME PLUGIN — BYPASS FREE

import random
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


# -------- FONT --------
def nezuko_style(text):
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return str(text).lower().translate(mapping)


# -------- ECONOMY CHECK --------
async def check_economy(update: Update):
    if update.effective_chat.type == "private":
        return True
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("<b>⚠️ For reopen use: /open</b>", parse_mode=ParseMode.HTML)
        return False
    return True


# -------- KILL --------
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update):
        return

    attacker = ensure_user_exists(update.effective_user)
    if attacker.get("status") == "dead":
        return await update.message.reply_text(nezuko_style("you are dead! revive first."))

    res = await resolve_target(update, context)
    victim = res[0] if isinstance(res, (list, tuple)) else res
    if not victim:
        return await update.message.reply_text(nezuko_style("reply to a victim!"))

    now = datetime.utcnow()
    expiry = victim.get("protection_expiry")

    # 🔒 HARD STOP
    if expiry is not None and expiry > now and update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("🛡️ " + nezuko_style("victim is protected right now!"))

    if victim.get("status") == "dead":
        return await update.message.reply_text(nezuko_style(f"{victim['name']} is already dead!"))

    reward = random.randint(100, 200)
    users_collection.update_one(
        {"user_id": victim["user_id"]},
        {"$set": {"status": "dead", "death_time": now}}
    )
    users_collection.update_one(
        {"user_id": attacker["user_id"]},
        {"$inc": {"balance": reward, "kills": 1}}
    )

    await update.message.reply_text(
        f"<b>{attacker['name'].upper()} killed {victim['name'].upper()}!</b>\n"
        f"<b>{nezuko_style('earned')}: {format_money(reward)}</b>",
        parse_mode=ParseMode.HTML
    )


# -------- ROB --------
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update):
        return

    user = ensure_user_exists(update.effective_user)
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text(nezuko_style("usage: reply with /rob <amount>"))

    amount = int(context.args[0])
    res = await resolve_target(update, context)
    target = res[0] if isinstance(res, (list, tuple)) else res

    now = datetime.utcnow()
    expiry = target.get("protection_expiry")

    # 🔒 HARD STOP
    if expiry is not None and expiry > now:
        return await update.message.reply_text("🛡️ " + nezuko_style("victim is protected right now!"))

    if target.get("balance", 0) < amount:
        return await update.message.reply_text(nezuko_style("target doesnt have enough money!"))

    users_collection.update_one({"user_id": target["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": amount}})

    await update.message.reply_text(
        f"<b>{user['name']} robbed {target['name']}!</b>\n"
        f"<b>looted: {format_money(amount)}</b>",
        parse_mode=ParseMode.HTML
    )


# -------- REVIVE --------
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update):
        return

    user = ensure_user_exists(update.effective_user)
    res = await resolve_target(update, context) if update.message.reply_to_message else user
    target = res[0] if isinstance(res, (list, tuple)) else res

    if target.get("status") == "alive":
        return await update.message.reply_text(nezuko_style("user is already alive!"))

    if user.get("balance", 0) < REVIVE_COST:
        return await update.message.reply_text(f"<b>❌ revive cost: {format_money(REVIVE_COST)}</b>", parse_mode=ParseMode.HTML)

    users_collection.update_one(
        {"user_id": target["user_id"]},
        {"$set": {"status": "alive", "death_time": None}}
    )
    users_collection.update_one(
        {"user_id": user["user_id"]},
        {"$inc": {"balance": -REVIVE_COST}}
    )

    await update.message.reply_text(nezuko_style(f"{target['name']} has been revived!"))


# -------- PROTECT --------
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update):
        return

    user = ensure_user_exists(update.effective_user)
    now = datetime.utcnow()

    if user.get("protection_expiry") and user["protection_expiry"] > now:
        return await update.message.reply_text("🛡️ " + nezuko_style("you are already protected!"))

    if not context.args:
        return await update.message.reply_text(nezuko_style("usage: /protect 1d | 2d"))

    choice = context.args[0].lower()
    cost, days = (PROTECT_2D_COST, 2) if choice == "2d" else (PROTECT_1D_COST, 1)

    if user.get("balance", 0) < cost:
        return await update.message.reply_text(f"<b>❌ need {format_money(cost)}</b>", parse_mode=ParseMode.HTML)

    expiry = now + timedelta(days=days)
    users_collection.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -cost}}
    )

    await update.message.reply_text("🛡️ " + nezuko_style(f"you are protected for {choice}"))
