# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Admin Plugin - Serif Italic Integrated

import html
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, UPSTREAM_REPO
from baka.utils import SUDO_USERS, get_mention, resolve_target, format_money, reload_sudoers, stylize_text
from baka.database import users_collection, sudoers_collection, groups_collection, reset_daily_activity, reset_weekly_activity

# --- HELP PANEL ---
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS: return
    msg = (
        f"🔐 <b>{stylize_text('Sudo Panel')}</b>\n\n"
        f"<b>💰 {stylize_text('Economy')}:</b>\n"
        "‣ /addcoins [amt] [user]\n"
        "‣ /rmcoins [amt] [user]\n"
        "‣ /freerevive [user]\n"
        "‣ /unprotect [user]\n\n"
        f"<b>🏆 {stylize_text('Competition')}:</b>\n"
        "‣ /resetstats daily\n"
        "‣ /resetstats weekly\n\n"
        f"<b>👑 {stylize_text('Owner Only')}:</b>\n"
        "‣ /update | /cleandb\n"
        "‣ /addsudo | /rmsudo\n"
        "‣ /sudolist"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- LEADERBOARD RESET ---
async def reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ <b>Owner only command!</b>", parse_mode=ParseMode.HTML)
    if not context.args:
        return await update.message.reply_text("⚠️ Use: <code>/resetstats daily</code> or <code>weekly</code>")

    mode = context.args[0].lower()
    if mode == "daily":
        reset_daily_activity()
        await update.message.reply_text(f"✨ {stylize_text('DAILY STATS RESET')}")
    elif mode == "weekly":
        reset_weekly_activity()
        await update.message.reply_text(f"👑 {stylize_text('WEEKLY STATS RESET')}")

# --- HANDLERS ---
async def addcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    if not context.args: return await update.message.reply_text("⚠️ Usage: /addcoins 100 @user")
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"Add {format_money(amount)} to {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")

async def rmcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    if not context.args: return await update.message.reply_text("⚠️ Usage: /rmcoins 100 @user")
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"Remove {format_money(amount)} from {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")

async def addsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Promote {get_mention(target)}?", "addsudo", str(target['user_id']))

async def rmsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Demote {get_mention(target)}?", "rmsudo", str(target['user_id']))

# --- UTILS ---
def parse_amount_and_target(args):
    amount = next((int(a) for a in args if a.isdigit()), 0)
    target = next((a for a in args if not a.isdigit() and not a.startswith('/')), None)
    return amount, target

async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ 𝐘𝐞𝐬", callback_data=f"cnf|{act}|{arg}"),
        InlineKeyboardButton("❌ 𝐍𝐨", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ {text}", reply_markup=kb, parse_mode=ParseMode.HTML)

# --- CALLBACK LOADER ---
async def confirm_handler(update, context):
    q = update.callback_query
    if q.from_user.id not in SUDO_USERS: return await q.answer("❌ Not for you!", show_alert=True)
    
    data = q.data.split("|")
    act, arg = data[1], data[2]
    if act == "cancel": return await q.message.edit_text("❌ Action Cancelled.")

    if act == "addcoins":
        uid, amt = int(arg), int(data[3])
        users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
        await q.message.edit_text(f"✅ Added {format_money(amt)} to <code>{uid}</code>.")
    elif act == "rmcoins":
        uid, amt = int(arg), int(data[3])
        users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
        await q.message.edit_text(f"✅ Removed {format_money(amt)} from <code>{uid}</code>.")
    elif act == "addsudo":
        sudoers_collection.update_one({"user_id": int(arg)}, {"$set": {"user_id": int(arg)}}, upsert=True)
        reload_sudoers()
        await q.message.edit_text(f"✅ <code>{arg}</code> is now Sudoer.")
    elif act == "cleandb":
        users_collection.delete_many({}); groups_collection.delete_many({})
        await q.message.edit_text("🗑️ <b>DATABASE WIPED!</b>")
