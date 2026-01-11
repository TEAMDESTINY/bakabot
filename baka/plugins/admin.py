# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Admin Plugin - Fully Synced Commands (Economy, System & Database)

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import get_mention, resolve_target, format_money, stylize_text
from baka.database import users_collection, sudoers_collection, groups_collection

# --- 🔐 AUTHORIZATION CHECK ---
def is_authorized(user_id):
    return user_id == OWNER_ID or user_id in SUDO_IDS

# --- 📋 SUDO HELP PANEL ---
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    msg = (
        f"🔐 <b>{stylize_text('Sudo Panel')}</b>\n\n"
        f"<b>💰 Economy:</b>\n"
        "🌹 /addcoins [amt] [user]\n"
        "🌹 /rmcoins [amt] [user]\n"
        "🌹 /freerevive [user]\n"
        "🌹 /unprotect [user]\n\n"
        f"<b>👑 Owner Only:</b>\n"
        "🌹 /addsudo [user] | /rmsudo [user]\n"
        "🌹 /sudolist\n"
        "🌹 /cleandb"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 💰 ECONOMY ACTIONS ---
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    if len(context.args) < 1:
        return await update.message.reply_text("❌ Usage: <code>/addcoins 1000 @user</code>", parse_mode=ParseMode.HTML)
    
    amount = int(context.args[0])
    target, err = await resolve_target(update, context)
    if target: 
        await ask(update, f"Add {format_money(amount)} to {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")

async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    if len(context.args) < 1:
        return await update.message.reply_text("❌ Usage: <code>/rmcoins 1000 @user</code>", parse_mode=ParseMode.HTML)
    
    amount = int(context.args[0])
    target, err = await resolve_target(update, context)
    if target: 
        await ask(update, f"Remove {format_money(amount)} from {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")

# --- 🛡️ SYSTEM ACTIONS ---
async def freerevive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, err = await resolve_target(update, context)
    if target: 
        await ask(update, f"Free Revive {get_mention(target)}?", "freerevive", str(target['user_id']))

async def unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, err = await resolve_target(update, context)
    if target: 
        await ask(update, f"Remove shield from {get_mention(target)}?", "unprotect", str(target['user_id']))

async def cleandb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await ask(update, "<b>WIPE DATABASE?</b> 🗑️\nThis will delete all users/groups!", "cleandb", "confirm")

# --- 👑 SUDO MGMT ---
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Make {get_mention(target)} a Sudoer?", "addsudo", str(target['user_id']))

async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Remove {get_mention(target)} from Sudoers?", "rmsudo", str(target['user_id']))

# --- 🛠️ UTILS ---
async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yes", callback_data=f"cnf|{act}|{arg}"), 
        InlineKeyboardButton("❌ No", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ <b>Wait!</b> {text}\nAre you sure?", parse_mode=ParseMode.HTML, reply_markup=kb)

# --- 🎯 CALLBACK HANDLER (FINAL SYNC) ---
async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not is_authorized(q.from_user.id): 
        return await q.answer("❌ Unauthorized!", show_alert=True)
    
    data = q.data.split("|")
    act = data[1]
    
    if act == "cancel": return await q.message.edit_text("❌ Action Cancelled.")

    try:
        # 💰 Economy
        if act == "addcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text(f"✅ Success: Added <b>{format_money(amt)}</b> to {uid}.")

        elif act == "rmcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
            await q.message.edit_text(f"✅ Success: Removed <b>{format_money(amt)}</b> from {uid}.")

        # 🛡️ System
        elif act == "freerevive":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"status": "alive", "death_time": None}})
            await q.message.edit_text(f"✨ User <code>{uid}</code> has been revived.")

        elif act == "unprotect":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"protection_expiry": None}})
            await q.message.edit_text(f"🛡️ Shield removed for <code>{uid}</code>.")

        # 👑 Sudo
        elif act == "addsudo":
            uid = int(data[2])
            sudoers_collection.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
            if uid not in SUDO_IDS: SUDO_IDS.append(uid)
            await q.message.edit_text(f"✅ <code>{uid}</code> is now a Sudoer.")

        elif act == "cleandb":
            users_collection.delete_many({})
            groups_collection.delete_many({})
            await q.message.edit_text("🗑️ <b>DATABASE WIPED SUCCESSFULLY!</b>")

    except Exception as e:
        await q.message.edit_text(f"❌ Error during execution: {e}")
