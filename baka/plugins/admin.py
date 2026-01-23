# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL ADMIN.PY — STABLE (NO CONFIRM HANDLER, NO CRASH)

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import resolve_target, format_money
from baka.database import users_collection, sudoers_collection, groups_collection


# ─── NEZUKO FONT ──────────────────────────────────────────────────────────────
def nezuko(text):
    clean = str(text).replace("<", "").replace(">", "")
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return f"<code>{clean.lower().translate(mapping)}</code>"


# ─── AUTH CHECK ───────────────────────────────────────────────────────────────
def is_authorized(user_id: int) -> bool:
    db_sudos = [s["user_id"] for s in sudoers_collection.find()]
    return user_id == OWNER_ID or user_id in SUDO_IDS or user_id in db_sudos


# ─── SAFE TARGET RESOLVER ─────────────────────────────────────────────────────
async def get_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await resolve_target(update, context)
    if not result or not isinstance(result, (list, tuple)):
        return None
    return result[0]


# ─── SUDO PANEL ───────────────────────────────────────────────────────────────
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    msg = (
        f"🔐 {nezuko('sudo panel')}\n\n"
        f"💰 <b>{nezuko('economy')}</b>\n"
        f"• {nezuko('/addcoins amt')}\n"
        f"• {nezuko('/rmcoins amt')}\n"
        f"• {nezuko('/freerevive')}\n"
        f"• {nezuko('/unprotect')}\n\n"
        f"👑 <b>{nezuko('sudo management')}</b>\n"
        f"• {nezuko('/addsudo')} | {nezuko('/rmsudo')}\n"
        f"• {nezuko('/sudolist')} | {nezuko('/cleandb')}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)


# ─── SUDO LIST ────────────────────────────────────────────────────────────────
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    sudos = list(sudoers_collection.find())
    msg = f"🛡️ {nezuko('sudoers list')}\n\n👑 OWNER: <code>{OWNER_ID}</code>\n"

    for s in sudos:
        if s["user_id"] != OWNER_ID:
            msg += f"• <code>{s['user_id']}</code>\n"

    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)


# ─── ADD / REMOVE SUDO ────────────────────────────────────────────────────────
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    target = await get_target(update, context)
    if not target:
        await update.message.reply_text("User not found.")
        return

    sudoers_collection.update_one(
        {"user_id": target["user_id"]},
        {"$set": {"user_id": target["user_id"]}},
        upsert=True
    )

    await update.message.reply_text(
        nezuko(f"{target['name']} added as sudo"),
        parse_mode=ParseMode.HTML
    )


async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    target = await get_target(update, context)
    if not target:
        await update.message.reply_text("User not found.")
        return

    sudoers_collection.delete_one({"user_id": target["user_id"]})

    await update.message.reply_text(
        nezuko(f"{target['name']} removed from sudo"),
        parse_mode=ParseMode.HTML
    )


# ─── ADD / REMOVE COINS ───────────────────────────────────────────────────────
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /addcoins 1000")
        return

    target = await get_target(update, context)
    if not target:
        await update.message.reply_text("User not found.")
        return

    amount = int(context.args[0])

    users_collection.update_one(
        {"user_id": target["user_id"]},
        {"$inc": {"balance": amount}},
        upsert=True
    )

    await update.message.reply_text(
        nezuko(f"added {format_money(amount)} to {target['name']}"),
        parse_mode=ParseMode.HTML
    )


async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not context.args:
        return

    target = await get_target(update, context)
    if not target:
        await update.message.reply_text("User not found.")
        return

    amount = int(context.args[0])

    users_collection.update_one(
        {"user_id": target["user_id"]},
        {"$inc": {"balance": -amount}}
    )

    await update.message.reply_text(
        nezuko(f"removed {format_money(amount)} from {target['name']}"),
        parse_mode=ParseMode.HTML
    )


# ─── UNPROTECT / REVIVE ───────────────────────────────────────────────────────
async def unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    target = await get_target(update, context)
    if not target:
        await update.message.reply_text("User not found.")
        return

    users_collection.update_one(
        {"user_id": target["user_id"]},
        {"$set": {"protection_expiry": None}}
    )

    await update.message.reply_text(nezuko("protection removed"), parse_mode=ParseMode.HTML)


async def freerevive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    target = await get_target(update, context)
    if not target:
        await update.message.reply_text("User not found.")
        return

    users_collection.update_one(
        {"user_id": target["user_id"]},
        {"$set": {"status": "alive"}}
    )

    await update.message.reply_text(nezuko("user revived"), parse_mode=ParseMode.HTML)


# ─── CLEAN DB (OWNER ONLY) ────────────────────────────────────────────────────
async def cleandb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    users_collection.delete_many({})
    groups_collection.delete_many({})

    await update.message.reply_text(
        nezuko("database wiped"),
        parse_mode=ParseMode.HTML
    )
