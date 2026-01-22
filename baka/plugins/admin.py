# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL ADMIN PLUGIN - NEZUKO MONOSPACE STYLE

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import resolve_target, format_money
from baka.database import users_collection, sudoers_collection

# --- 🎨 NEZUKO FONT HELPER ---
def nezuko(text):
    """Converts text to Small Caps and wraps in Monospace."""
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return f"<code>{text.lower().translate(mapping)}</code>"

# --- 🔐 AUTH CHECK ---
def is_authorized(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_IDS

# --- 📋 HELP PANEL ---
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    msg = (
        f"🔐 {nezuko('Sudo Panel')}\n\n"
        f"<b>💰 {nezuko('Economy')}</b>\n"
        f"🌹 {nezuko('/addcoins <amt> <user>')}\n"
        f"🌹 {nezuko('/rmcoins <amt> <user>')}\n"
        f"🌹 {nezuko('/freerevive <user>')}\n"
        f"🌹 {nezuko('/unprotect <user>')}\n\n"
        f"<b>👑 {nezuko('Owner Only')}</b>\n"
        f"🌹 {nezuko('/addsudo <user>')}\n"
        f"🌹 {nezuko('/rmsudo <user>')}\n"
        f"🌹 {nezuko('/sudolist')}\n"
        f"🌹 {nezuko('/cleandb')}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 👑 SUDO MGMT ---
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    target, _ = await resolve_target(update, context)
    if target:
        await ask(update, nezuko(f"make {target['name']} a sudo?"), "addsudo", str(target["user_id"]))

async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    target, _ = await resolve_target(update, context)
    if target:
        await ask(update, nezuko(f"remove {target['name']} from sudo?"), "rmsudo", str(target["user_id"]))

async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    msg = f"🛡️ {nezuko('Sudoers')}\n\n"
    msg += f"👑 ᴏᴡɴᴇʀ: <code>{OWNER_ID}</code>\n"
    for s in sudoers_collection.find():
        msg += f"• <code>{s['user_id']}</code>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 💰 ECONOMY ---
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    try:
        amount = int(context.args[0])
        target, _ = await resolve_target(update, context)
        if target:
            await ask(update, nezuko(f"add {format_money(amount)} to {target['name']}?"), "addcoins", f"{target['user_id']}|{amount}")
    except:
        await update.message.reply_text(nezuko("❌ usage: /addcoins 1000 @user"), parse_mode=ParseMode.HTML)

async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    try:
        amount = int(context.args[0])
        target, _ = await resolve_target(update, context)
        if target:
            await ask(update, nezuko(f"remove {format_money(amount)} from {target['name']}?"), "rmcoins", f"{target['user_id']}|{amount}")
    except:
        await update.message.reply_text(nezuko("❌ usage: /rmcoins 1000 @user"), parse_mode=ParseMode.HTML)

async def freerevive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, _ = await resolve_target(update, context)
    if target:
        await ask(update, nezuko(f"free revive {target['name']}?"), "freerevive", str(target["user_id"]))

async def unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, _ = await resolve_target(update, context)
    if target:
        await ask(update, nezuko(f"remove shield from {target['name']}?"), "unprotect", str(target["user_id"]))

async def cleandb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await ask(update, nezuko("wipe entire database?"), "cleandb", "confirm")

# --- 🎯 CONFIRMATION ENGINE ---
async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ ʏᴇs", callback_data=f"cnf|{act}|{arg}"),
        InlineKeyboardButton("❌ ɴᴏ", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ {text}\n<b>{nezuko('confirm?')}</b>", parse_mode=ParseMode.HTML, reply_markup=kb)

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not is_authorized(q.from_user.id): return

    _, act, arg = q.data.split("|")
    if act == "cancel":
        return await q.message.edit_text(nezuko("❌ cancelled."), parse_mode=ParseMode.HTML)

    try:
        if act == "addsudo":
            uid = int(arg)
            sudoers_collection.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
            SUDO_IDS.add(uid)
            await q.message.edit_text(nezuko(f"✅ {uid} added as sudo."), parse_mode=ParseMode.HTML)

        elif act == "rmsudo":
            uid = int(arg)
            sudoers_collection.delete_one({"user_id": uid})
            SUDO_IDS.discard(uid)
            await q.message.edit_text(nezuko(f"❌ {uid} removed from sudo."), parse_mode=ParseMode.HTML)

        elif act == "addcoins":
            uid, amt = map(int, arg.split("|"))
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text(nezuko("✅ coins added."), parse_mode=ParseMode.HTML)

        elif act == "rmcoins":
            uid, amt = map(int, arg.split("|"))
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
            await q.message.edit_text(nezuko("✅ coins removed."), parse_mode=ParseMode.HTML)

        elif act == "freerevive":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"status": "alive"}})
            await q.message.edit_text(nezuko("💖 user revived."), parse_mode=ParseMode.HTML)

        elif act == "unprotect":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"protection_expiry": None}})
            await q.message.edit_text(nezuko("🛡️ protection removed."), parse_mode=ParseMode.HTML)

        elif act == "cleandb":
            users_collection.delete_many({})
            sudoers_collection.delete_many({})
            await q.message.edit_text(nezuko("💥 database wiped."), parse_mode=ParseMode.HTML)

    except Exception as e:
        await q.message.edit_text(f"❌ {nezuko('error')}: <code>{e}</code>", parse_mode=ParseMode.HTML)
