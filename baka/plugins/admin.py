# Copyright (c) 2026
# Telegram: @WTF_Phantom <DevixOP>
# FINAL ADMIN PLUGIN (STABLE)

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import resolve_target, format_money
from baka.database import users_collection, sudoers_collection

# ───────────────────── AUTH ─────────────────────

def is_authorized(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_IDS

# ───────────────────── HELP ─────────────────────

async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    msg = (
        "🔐 <b>Sudo Panel</b>\n\n"
        "<b>💰 Economy</b>\n"
        "/addcoins <amt> <user>\n"
        "/rmcoins <amt> <user>\n"
        "/freerevive <user>\n"
        "/unprotect <user>\n\n"
        "<b>👑 Owner Only</b>\n"
        "/addsudo <user>\n"
        "/rmsudo <user>\n"
        "/sudolist\n"
        "/cleandb"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# ───────────────────── SUDO MGMT ─────────────────────

async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    target, _ = await resolve_target(update, context)
    if not target:
        return

    await ask(
        update,
        f"Make <b>{target['name']}</b> a sudo?",
        "addsudo",
        str(target["user_id"])
    )

async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    target, _ = await resolve_target(update, context)
    if not target:
        return

    await ask(
        update,
        f"Remove <b>{target['name']}</b> from sudo?",
        "rmsudo",
        str(target["user_id"])
    )

async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    msg = "🛡️ <b>Sudoers</b>\n\n"
    msg += f"👑 Owner: <code>{OWNER_ID}</code>\n"

    for s in sudoers_collection.find():
        msg += f"• <code>{s['user_id']}</code>\n"

    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# ───────────────────── ECONOMY ─────────────────────

async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    try:
        amount = int(context.args[0])
        target, _ = await resolve_target(update, context)
        if not target:
            return

        await ask(
            update,
            f"Add {format_money(amount)} to <b>{target['name']}</b>?",
            "addcoins",
            f"{target['user_id']}|{amount}"
        )
    except:
        await update.message.reply_text(
            "❌ <b>Usage:</b> /addcoins 1000 @user",
            parse_mode=ParseMode.HTML
        )

async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    try:
        amount = int(context.args[0])
        target, _ = await resolve_target(update, context)
        if not target:
            return

        await ask(
            update,
            f"Remove {format_money(amount)} from <b>{target['name']}</b>?",
            "rmcoins",
            f"{target['user_id']}|{amount}"
        )
    except:
        await update.message.reply_text(
            "❌ <b>Usage:</b> /rmcoins 1000 @user",
            parse_mode=ParseMode.HTML
        )

async def freerevive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    target, _ = await resolve_target(update, context)
    if target:
        await ask(update, f"Free revive <b>{target['name']}</b>?", "freerevive", str(target["user_id"]))

async def unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    target, _ = await resolve_target(update, context)
    if target:
        await ask(update, f"Remove shield from <b>{target['name']}</b>?", "unprotect", str(target["user_id"]))

async def cleandb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await ask(update, "<b>WIPE ENTIRE DATABASE?</b>", "cleandb", "confirm")

# ───────────────────── CONFIRM HANDLER ─────────────────────

async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yes", callback_data=f"cnf|{act}|{arg}"),
        InlineKeyboardButton("❌ No", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(
        f"⚠️ {text}\n<b>Confirm?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=kb
    )

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not is_authorized(q.from_user.id):
        return

    _, act, arg = q.data.split("|")

    if act == "cancel":
        return await q.message.edit_text("❌ Cancelled.")

    try:
        if act == "addsudo":
            uid = int(arg)
            sudoers_collection.update_one(
                {"user_id": uid},
                {"$set": {"user_id": uid}},
                upsert=True
            )
            SUDO_IDS.add(uid)
            await q.message.edit_text(f"✅ <code>{uid}</code> added as sudo.", parse_mode=ParseMode.HTML)

        elif act == "rmsudo":
            uid = int(arg)
            sudoers_collection.delete_one({"user_id": uid})
            SUDO_IDS.discard(uid)
            await q.message.edit_text(f"❌ <code>{uid}</code> removed from sudo.", parse_mode=ParseMode.HTML)

        elif act == "addcoins":
            uid, amt = map(int, arg.split("|"))
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text("✅ Coins added.")

        elif act == "rmcoins":
            uid, amt = map(int, arg.split("|"))
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
            await q.message.edit_text("✅ Coins removed.")

        elif act == "freerevive":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"status": "alive"}})
            await q.message.edit_text("💖 User revived.")

        elif act == "unprotect":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"protection_expiry": None}})
            await q.message.edit_text("🛡️ Protection removed.")

        elif act == "cleandb":
            users_collection.delete_many({})
            sudoers_collection.delete_many({})
            await q.message.edit_text("💥 Database wiped.")

    except Exception as e:
        await q.message.edit_text(f"❌ Error: <code>{e}</code>", parse_mode=ParseMode.HTML)
