# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL ADMIN PLUGIN - STABLE VERSION (NO MISSING ATTRIBUTES)

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import resolve_target, format_money
from baka.database import users_collection, sudoers_collection, groups_collection

# --- 🎨 NEZUKO FONT HELPER ---
def nezuko(text):
    """Converts text to Small Caps and Monospace."""
    clean_text = str(text).replace("<", "").replace(">", "")
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return f"<code>{clean_text.lower().translate(mapping)}</code>"

# --- 🔐 AUTH CHECK ---
def is_authorized(user_id: int) -> bool:
    """Checks if user is Owner or in DB Sudoers."""
    db_sudos = [s['user_id'] for s in sudoers_collection.find()]
    return user_id == OWNER_ID or user_id in SUDO_IDS or user_id in db_sudos

# --- 📋 1. SUDO HELP PANEL ---
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    msg = (
        f"🔐 {nezuko('sudo panel')}\n\n"
        f"💰 <b>{nezuko('economy')}</b>\n"
        f"🌹 {nezuko('/addcoins amt')}\n"
        f"🌹 {nezuko('/rmcoins amt')}\n"
        f"🌹 {nezuko('/freerevive')}\n"
        f"🌹 {nezuko('/unprotect')}\n\n"
        f"👑 <b>{nezuko('owner only')}</b>\n"
        f"🌹 {nezuko('/addsudo')} | {nezuko('/rmsudo')}\n"
        f"🌹 {nezuko('/sudolist')} | {nezuko('/cleandb')}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 👑 2. SUDO LIST (FIXES THE ATTRIBUTEERROR) ---
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all authorized sudo users."""
    if not is_authorized(update.effective_user.id): return
    sudos = list(sudoers_collection.find())
    msg = f"🛡️ {nezuko('sudoers list')}\n\n👑 ᴏᴡɴᴇʀ: <code>{OWNER_ID}</code>\n"
    for s in sudos: 
        msg += f"• <code>{s['user_id']}</code>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🛡️ 3. UNPROTECT ---
async def unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    resolved = await resolve_target(update, context)
    target = resolved[0] if isinstance(resolved, (tuple, list)) else resolved
    if target:
        await ask(update, f"{nezuko('remove shield from')} {target['name']}?", "unprotect", str(target["user_id"]))

# --- 👑 4. ADD/REMOVE SUDO ---
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    resolved = await resolve_target(update, context)
    target = resolved[0] if isinstance(resolved, (tuple, list)) else resolved
    if target:
        await ask(update, f"{nezuko('make')} {target['name']} {nezuko('a sudo')}?", "addsudo", str(target["user_id"]))

async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    resolved = await resolve_target(update, context)
    target = resolved[0] if isinstance(resolved, (tuple, list)) else resolved
    if target:
        await ask(update, f"{nezuko('remove')} {target['name']} {nezuko('from sudo')}?", "rmsudo", str(target["user_id"]))

# --- 💰 5. ADD/REMOVE COINS ---
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    try:
        if not context.args: return await update.message.reply_text(nezuko("❌ usage: /addcoins 1000"))
        amount = int(context.args[0])
        resolved = await resolve_target(update, context)
        target = resolved[0] if isinstance(resolved, (tuple, list)) else resolved
        if target:
            await ask(update, f"{nezuko('add')} {format_money(amount)} {nezuko('to')} {target['name']}?", "addcoins", f"{target['user_id']}|{amount}")
    except: await update.message.reply_text(nezuko("❌ usage: /addcoins 1000"))

async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    try:
        amount = int(context.args[0])
        resolved = await resolve_target(update, context)
        target = resolved[0] if isinstance(resolved, (tuple, list)) else resolved
        if target:
            await ask(update, f"{nezuko('remove')} {format_money(amount)} {nezuko('from')} {target['name']}?", "rmcoins", f"{target['user_id']}|{amount}")
    except: pass

# --- 🛡️ 6. FREE REVIVE ---
async def freerevive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    resolved = await resolve_target(update, context)
    target = resolved[0] if isinstance(resolved, (tuple, list)) else resolved
    if target:
        await ask(update, f"{nezuko('free revive')} {target['name']}?", "freerevive", str(target["user_id"]))

# --- 👑 7. CLEAN DATABASE ---
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
    try:
        data = q.data.split("|")
        act, arg = data[1], data[2]
        if act == "cancel": return await q.message.edit_text(nezuko("❌ cancelled."))
        
        if act == "addcoins":
            uid, amt = map(int, arg.split("|"))
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text(nezuko(f"✅ added {amt} coins."))
        elif act == "addsudo":
            uid = int(arg)
            sudoers_collection.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
            await q.message.edit_text(nezuko(f"✅ {uid} added as sudo."))
        elif act == "rmsudo":
            uid = int(arg)
            sudoers_collection.delete_one({"user_id": uid})
            await q.message.edit_text(nezuko(f"❌ {uid} removed from sudo."))
        elif act == "unprotect":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"protection_expiry": None}})
            await q.message.edit_text(nezuko("🛡️ protection removed."))
        elif act == "freerevive":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"status": "alive"}})
            await q.message.edit_text(nezuko("💖 user revived."))
        elif act == "cleandb":
            users_collection.delete_many({}); groups_collection.delete_many({})
            await q.message.edit_text(nezuko("💥 database wiped."))
    except Exception as e: await q.message.edit_text(f"❌ {nezuko('error')}: {e}")
