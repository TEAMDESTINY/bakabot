# Copyright (c) 2025 ...
# (same header left unchanged)

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from baka.config import (
    PROTECT_1D_COST, PROTECT_2D_COST, REVIVE_COST,
    AUTO_REVIVE_HOURS, OWNER_ID
)

from baka.utils import (
    ensure_user_exists, resolve_target, is_protected,
    get_active_protection, format_time, format_money,
    get_mention, check_auto_revive, stylize_text,
    add_xp, get_user_badge
)

from baka.database import users_collection
from baka.plugins.chatbot import ask_mistral_raw


# XP VALUES
XP_ROB = 20
XP_KILL = 40
XP_MESSAGE = 3


# --------------------------------------------------------------------
#                          AI Narration
# --------------------------------------------------------------------
async def get_narrative(action_type, attacker_mention, target_mention):
    if action_type == 'kill':
        prompt = "Write a funny, savage kill message where 'P1' kills 'P2'. Max 15 words. Hinglish."
    elif action_type == 'rob':
        prompt = "Write a funny robbery message where 'P1' steals from 'P2'. Max 15 words. Hinglish."
    else:
        return "P1 interaction P2."

    res = await ask_mistral_raw("Game Narrator", prompt, 50)
    text = res if res and "P1" in res else f"P1 {action_type} P2!"

    return text.replace("P1", attacker_mention).replace("P2", target_mention)


# --------------------------------------------------------------------
#                                KILL
# --------------------------------------------------------------------
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):

    attacker = ensure_user_exists(update.effective_user)
    target, error = await resolve_target(update, context)

    if not target:
        return await update.message.reply_text(
            error or "⚠️ Reply or Tag someone to kill.",
            parse_mode=ParseMode.HTML
        )

    # Validations
    if target.get('is_bot'):
        return await update.message.reply_text("🤖 Bot cannot be killed.", parse_mode=ParseMode.HTML)

    if target['user_id'] == OWNER_ID:
        return await update.message.reply_text("🛡 Owner cannot be killed.", parse_mode=ParseMode.HTML)

    if attacker['status'] == 'dead':
        return await update.message.reply_text("💀 You are dead! Wait or /revive.", parse_mode=ParseMode.HTML)

    if target['user_id'] == attacker['user_id']:
        return await update.message.reply_text("🤦 Self kill not allowed.", parse_mode=ParseMode.HTML)

    if target['status'] == 'dead':
        return await update.message.reply_text("⚰ Already dead.", parse_mode=ParseMode.HTML)

    expiry = get_active_protection(target)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(
            f"🛡 Protected for <code>{format_time(rem)}</code>.",
            parse_mode=ParseMode.HTML
        )

    # Kill chance (1/8)
    if random.randint(1, 8) != 1:
        return await update.message.reply_text("❌ Kill failed.", parse_mode=ParseMode.HTML)

    # Kill successful
    base_reward = random.randint(100, 200)
    users_collection.update_one(
        {"user_id": target["user_id"]},
        {"$set": {"status": "dead", "death_time": datetime.utcnow()}}
    )
    users_collection.update_one(
        {"user_id": attacker["user_id"]},
        {"$inc": {"kills": 1, "balance": base_reward}}
    )

    # XP ADD
    leveled, level, new_xp = add_xp(attacker["user_id"], XP_KILL)
    badge = get_user_badge(level)

    lvl_text = f"\n🎉 LEVEL UP → <b>{level}</b> {badge}" if leveled else ""

    # Narration
    narration = await get_narrative("kill", get_mention(attacker), get_mention(target))

    await update.message.reply_text(
        f"🔪 <b>{stylize_text('MURDER')}</b>\n\n"
        f"📝 <i>{narration}</i>\n\n"
        f"😈 Killer: {get_mention(attacker)}\n"
        f"💀 Victim: {get_mention(target)}\n"
        f"💵 Looted: <code>{format_money(base_reward)}</code>\n"
        f"🏅 XP Gained: <b>{XP_KILL}</b>{lvl_text}",
        parse_mode=ParseMode.HTML
    )


# --------------------------------------------------------------------
#                                 ROB
# --------------------------------------------------------------------
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):

    attacker = ensure_user_exists(update.effective_user)

    if not context.args:
        return await update.message.reply_text(
            "⚠ Usage: <code>/rob 100 @user</code>",
            parse_mode=ParseMode.HTML
        )

    try:
        amount = int(context.args[0])
    except:
        return await update.message.reply_text("Invalid amount!", parse_mode=ParseMode.HTML)

    target_arg = context.args[1] if len(context.args) > 1 else None
    target, error = await resolve_target(update, context, specific_arg=target_arg)

    if not target:
        return await update.message.reply_text(error or "Tag someone!", parse_mode=ParseMode.HTML)

    if target.get("is_bot") or target["user_id"] == OWNER_ID:
        return await update.message.reply_text("🛡 Protected entity.", parse_mode=ParseMode.HTML)

    if attacker["status"] == "dead":
        return await update.message.reply_text("💀 Dead men steal no coins.", parse_mode=ParseMode.HTML)

    if attacker["user_id"] == target["user_id"]:
        return await update.message.reply_text("🤦 No.", parse_mode=ParseMode.HTML)

    expiry = get_active_protection(target)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(
            f"🛡 Target Shielded for <code>{format_time(rem)}</code>.",
            parse_mode=ParseMode.HTML
        )

    if target["balance"] < amount:
        return await update.message.reply_text("📉 Target too poor.", parse_mode=ParseMode.HTML)

    # Transfer
    users_collection.update_one({"user_id": target["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": attacker["user_id"]}, {"$inc": {"balance": amount}})

    # XP ADD
    leveled, level, new_xp = add_xp(attacker["user_id"], XP_ROB)
    badge = get_user_badge(level)
    lvl_text = f"\n🎉 LEVEL UP → <b>{level}</b> {badge}" if leveled else ""

    narration = await get_narrative("rob", get_mention(attacker), get_mention(target))

    await update.message.reply_text(
        f"💰 <b>{stylize_text('ROBBERY')}</b>\n\n"
        f"📝 <i>{narration}</i>\n"
        f"😈 Thief: {get_mention(attacker)}\n"
        f"💸 Stolen: <code>{format_money(amount)}</code>\n"
        f"🏅 XP Gained: <b>{XP_ROB}</b>{lvl_text}",
        parse_mode=ParseMode.HTML
    )


# --------------------------------------------------------------------
#                               PROTECT
# --------------------------------------------------------------------
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)

    if not context.args:
        return await update.message.reply_text(
            f"🛡 Usage: /protect 1d",
            parse_mode=ParseMode.HTML
        )

    dur = context.args[0].lower()
    if dur == "1d":
        cost, days = PROTECT_1D_COST, 1
    elif dur == "2d":
        cost, days = PROTECT_2D_COST, 2
    else:
        return await update.message.reply_text("Only 1d/2d allowed.", parse_mode=ParseMode.HTML)

    target_arg = context.args[1] if len(context.args) > 1 else None
    target, _ = await resolve_target(update, context, specific_arg=target_arg)
    if not target:
        target = sender

    expiry = get_active_protection(target)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(
            f"🛡 Already protected for <code>{format_time(rem)}</code>.",
            parse_mode=ParseMode.HTML
        )

    if sender["balance"] < cost:
        return await update.message.reply_text(
            f"❌ Need {format_money(cost)}.",
            parse_mode=ParseMode.HTML
        )

    users_collection.update_one({"user_id": sender["user_id"]}, {"$inc": {"balance": -cost}})
    expiry_dt = datetime.utcnow() + timedelta(days=days)

    users_collection.update_one(
        {"user_id": target["user_id"]},
        {"$set": {"protection_expiry": expiry_dt}}
    )

    await update.message.reply_text(
        f"🛡 Shield Active for {days}d.",
        parse_mode=ParseMode.HTML
    )


# --------------------------------------------------------------------
#                              REVIVE
# --------------------------------------------------------------------
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reviver = ensure_user_exists(update.effective_user)
    target, _ = await resolve_target(update, context)
    if not target:
        target = reviver

    if target["status"] == "alive":
        return await update.message.reply_text("✨ Already alive.", parse_mode=ParseMode.HTML)

    if check_auto_revive(target):
        return await update.message.reply_text(
            "✨ Auto revived!",
            parse_mode=ParseMode.HTML
        )

    if reviver["balance"] < REVIVE_COST:
        return await update.message.reply_text(
            f"Need {format_money(REVIVE_COST)}.",
            parse_mode=ParseMode.HTML
        )

    users_collection.update_one({"user_id": reviver["user_id"]}, {"$inc": {"balance": -REVIVE_COST}})
    users_collection.update_one({"user_id": OWNER_ID}, {"$inc": {"balance": REVIVE_COST}})
    users_collection.update_one({"user_id": target["user_id"]}, {"$set": {"status": "alive", "death_time": None}})

    await update.message.reply_text(
        f"💖 Revived {get_mention(target)}.",
        parse_mode=ParseMode.HTML
    )


# --------------------------------------------------------------------
#                    AUTO XP ON EVERY MESSAGE
# --------------------------------------------------------------------
async def handle_message_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = ensure_user_exists(update.effective_user)

    if user["is_bot"]:
        return

    leveled, level, xp = add_xp(user["user_id"], XP_MESSAGE)

    if leveled:
        badge = get_user_badge(level)
        await update.message.reply_text(
            f"🎉 LEVEL UP → <b>{level}</b> {badge}",
            parse_mode=ParseMode.HTML
        )
