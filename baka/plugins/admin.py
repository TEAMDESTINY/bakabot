# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Fixed Admin Plugin - All Commands Authorized for Owner & Sudo

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import get_mention, resolve_target, format_money, stylize_text
from baka.database import users_collection, sudoers_collection, groups_collection

# --- 🔐 AUTHORIZATION CHECK ---
def is_authorized(user_id):
    """Owner aur Sudo users ko authorize karta hai."""
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
        "🌹 /cleandb\n"
        "🌹 /addsudo | /rmsudo\n"
        "🌹 /sudolist"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 💰 ACTIONS ---
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"Add {format_money(amount)} to {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")

async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"Remove {format_money(amount)} from {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")

async def freerevive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Free Revive {get_mention(target)}?", "freerevive", str(target['user_id']))

async def unprotect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id): return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Remove shield from {get_mention(target)}?", "unprotect", str(target['user_id']))

async def cleandb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await ask(update, "<b>WIPE DATABASE?</b> 🗑️", "cleandb", "confirm")

# --- 🛠️ UTILS ---
def parse_amount_and_target(args):
    amount = next((int(a) for a in args if a.isdigit()), None)
    target = next((a for a in args if not a.isdigit()), None)
    return amount, target

async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yes", callback_data=f"cnf|{act}|{arg}"), 
        InlineKeyboardButton("❌ No", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ <b>Wait!</b> {text}\nAre you sure?", parse_mode=ParseMode.HTML, reply_markup=kb)

# --- 🎯 CALLBACK HANDLER (FIXED) ---
async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not is_authorized(q.from_user.id): 
        return await q.answer("❌ Unauthorized!", show_alert=True)
    
    data = q.data.split("|")
    act = data[1]
    
    if act == "cancel": return await q.message.edit_text("❌ Action Cancelled.")

    try:
        # 1. FIXED: Add Coins
        if act == "addcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text(f"✅ Added {format_money(amt)} to {uid}.")
            
        # 2. FIXED: Remove Coins
        elif act == "rmcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
            await q.message.edit_text(f"🗑️ Removed {format_money(amt)} from {uid}.")

        # 3. FIXED: Free Revive
        elif act == "freerevive":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"status": "alive", "death_time": None, "auto_revive_at": None}})
            await q.message.edit_text(f"✨ User {uid} has been revived for free.")

        # 4. FIXED: Unprotect
        elif act == "unprotect":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"protection_expiry": None}})
            await q.message.edit_text(f"🛡️ Protection shield removed for {uid}.")

        # 5. FIXED: Clean DB
        elif act == "cleandb":
            users_collection.delete_many({})
            groups_collection.delete_many({})
            await q.message.edit_text("🗑️ <b>Database has been completely wiped!</b>")

    except Exception as e:
        await q.message.edit_text(f"❌ Error: {e}")
