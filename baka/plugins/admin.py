# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Admin Plugin - Unfree Command Removed

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, SUDO_IDS
from baka.utils import get_mention, resolve_target, format_money
from baka.database import users_collection, sudoers_collection, groups_collection

def is_authorized(user_id):
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
        uid = int(data[2])
        if act == "addcoins":
            amt = int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text(f"<b>✅ Added coins to {uid}.</b>", parse_mode=ParseMode.HTML)
        elif act == "rmcoins":
            amt = int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
            await q.message.edit_text(f"<b>✅ Removed coins from {uid}.</b>", parse_mode=ParseMode.HTML)
        elif act == "freerevive":
            users_collection.update_one({"user_id": uid}, {"$set": {"status": "alive"}})
            await q.message.edit_text(f"<b>✨ User {uid} revived.</b>", parse_mode=ParseMode.HTML)
        elif act == "unprotect":
            users_collection.update_one({"user_id": uid}, {"$set": {"protection_expiry": None}})
            await q.message.edit_text(f"<b>🛡️ Shield removed for {uid}.</b>", parse_mode=ParseMode.HTML)
    except Exception as e: await q.message.edit_text(f"<b>❌ Error: {e}</b>", parse_mode=ParseMode.HTML)
