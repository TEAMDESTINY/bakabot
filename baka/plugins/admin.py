# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Admin Plugin - Fixed AttributeError (addsudo/rmsudo added)

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import get_mention, resolve_target, format_money
from baka.database import users_collection, sudoers_collection, groups_collection

def is_authorized(user_id):
    """Checks if the user is the Bot Owner or in the Sudo list."""
    return user_id == OWNER_ID or user_id in SUDO_IDS

async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    msg = (
        "🔐 <b>Sudo Panel</b>\n\n"
        "<b>💰 Economy:</b>\n"
        "🌹 /addcoins [amt] [user]\n"
        "🌹 /rmcoins [amt] [user]\n"
        "🌹 /freerevive [user]\n"
        "🌹 /unprotect [user]\n\n"
        "<b>👑 Owner Only:</b>\n"
        "🌹 /addsudo [user] | /rmsudo [user]\n"
        "🌹 /sudolist\n"
        "🌹 /cleandb"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 👑 SUDO MANAGEMENT (FIXES THE CRASH) ---
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds a user to sudo list."""
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: 
        await ask(update, f"Make {target.get('name')} a Sudoer?", "addsudo", str(target['user_id']))

async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Removes a user from sudo list."""
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: 
        await ask(update, f"Remove {target.get('name')} from Sudoers?", "rmsudo", str(target['user_id']))

async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all sudo users."""
    if not is_authorized(update.effective_user.id): return
    sudos = list(sudoers_collection.find())
    msg = f"🛡️ <b>Sudoers List</b>\n\n"
    msg += f"👑 <b>Owner:</b> <code>{OWNER_ID}</code>\n"
    for s in sudos:
        msg += f"✨ <b>Sudo:</b> <code>{s['user_id']}</code>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 💰 ECONOMY & OTHERS ---
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    try:
        amount = int(context.args[0])
        target, _ = await resolve_target(update, context)
        if target: await ask(update, f"Add {format_money(amount)} to {target.get('name')}?", "addcoins", f"{target['user_id']}|{amount}")
    except: await update.message.reply_text("<b>❌ Usage: /addcoins 1000 @user</b>", parse_mode=ParseMode.HTML)

async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    try:
        amount = int(context.args[0])
        target, _ = await resolve_target(update, context)
        if target: await ask(update, f"Remove {format_money(amount)} from {target.get('name')}?", "rmcoins", f"{target['user_id']}|{amount}")
    except: await update.message.reply_text("<b>❌ Usage: /rmcoins 1000 @user</b>", parse_mode=ParseMode.HTML)

async def freerevive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, _ = await resolve_target(update, context)
    if target: await ask(update, f"Free Revive {target.get('name')}?", "freerevive", str(target['user_id']))

async def unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, _ = await resolve_target(update, context)
    if target: await ask(update, f"Remove shield from {target.get('name')}?", "unprotect", str(target['user_id']))

async def cleandb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await ask(update, "<b>WIPE DATABASE?</b>", "cleandb", "confirm")

# --- 🛠️ UTILS & CALLBACK ---
async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yes", callback_data=f"cnf|{act}|{arg}"), 
        InlineKeyboardButton("❌ No", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ <b>Wait!</b> {text}\nAre you sure?", parse_mode=ParseMode.HTML, reply_markup=kb)

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer() 
    if not is_authorized(q.from_user.id): return
    data = q.data.split("|")
    act = data[1]
    if act == "cancel": return await q.message.edit_text("<b>❌ Action Cancelled.</b>", parse_mode=ParseMode.HTML)
    
    try:
        if act == "addsudo":
            uid = int(data[2])
            sudoers_collection.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
            if uid not in SUDO_IDS: SUDO_IDS.append(uid)
            await q.message.edit_text(f"<b>✅ {uid} is now a Sudoer.</b>", parse_mode=ParseMode.HTML)
        # ... (Baaki saare acts: addcoins, rmcoins, etc. purane logic ki tarah hi rahenge)
    except Exception as e: await q.message.edit_text(f"<b>❌ Error: {e}</b>", parse_mode=ParseMode.HTML)
