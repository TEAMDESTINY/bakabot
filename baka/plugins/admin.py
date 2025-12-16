# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Admin Plugin - Serif Italic + All Handlers Fixed

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

# --- PERMISSION CHECK ---
def is_sudo(user_id):
    return user_id == OWNER_ID or user_id in SUDO_USERS

# --- HELP PANEL ---
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id): return
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

# --- ECONOMY ACTIONS ---
async def addcoins(update, context):
    if not is_sudo(update.effective_user.id): return
    if not context.args: return await update.message.reply_text("⚠️ 𝑼𝒔𝒂𝒈𝒆: <code>/addcoins 100 @user</code>")
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"𝑨𝒅𝒅 {format_money(amount)} 𝒕𝒐 {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")

async def rmcoins(update, context):
    if not is_sudo(update.effective_user.id): return
    if not context.args: return await update.message.reply_text("⚠️ 𝑼𝒔𝒂𝒈𝒆: <code>/rmcoins 100 @user</code>")
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"𝑹𝒆𝒎𝒐𝒗𝒆 {format_money(amount)} 𝒇𝒓𝒐𝒎 {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")

async def freerevive(update, context):
    if not is_sudo(update.effective_user.id): return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"𝑭𝒓𝒆𝒆 𝑹𝒆𝒗𝒊𝒗𝒆 {get_mention(target)}?", "freerevive", str(target['user_id']))

async def unprotect(update, context):
    if not is_sudo(update.effective_user.id): return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"𝑹𝒆𝒎𝒐𝒗𝒆 𝒔𝒉𝒊𝒆𝒍𝒅 𝒇𝒓𝒐𝒎 {get_mention(target)}?", "unprotect", str(target['user_id']))

# --- MANAGEMENT ---
async def reset_stats(update, context):
    if update.effective_user.id != OWNER_ID: return
    mode = context.args[0].lower() if context.args else ""
    if mode == "daily":
        reset_daily_activity()
        await update.message.reply_text(f"✨ {stylize_text('DAILY STATS RESET')}")
    elif mode == "weekly":
        reset_weekly_activity()
        await update.message.reply_text(f"👑 {stylize_text('WEEKLY STATS RESET')}")

async def sudolist(update, context):
    if not is_sudo(update.effective_user.id): return
    msg = f"👑 <b>{stylize_text('Owner & Sudoers')}:</b>\n\n"
    for uid in SUDO_USERS:
        u_doc = users_collection.find_one({"user_id": uid})
        role = "𝑶𝒘𝒏𝒆𝒓" if uid == OWNER_ID else "𝑺𝒖𝒅𝒐𝒆𝒓"
        msg += f"• {get_mention(u_doc) if u_doc else uid} ({role})\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def update_bot(update, context):
    if update.effective_user.id != OWNER_ID: return
    msg = await update.message.reply_text("🔄 𝑼𝒑𝒅𝒂𝒕𝒊𝒏𝒈...")
    os.execl(sys.executable, sys.executable, "Ryan.py")

# --- UTILS & CALLBACK ---
def parse_amount_and_target(args):
    amount = next((int(a) for a in args if a.isdigit()), 0)
    target = next((a for a in args if not a.isdigit()), None)
    return amount, target

async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ 𝒀𝒆𝒔", callback_data=f"cnf|{act}|{arg}"), InlineKeyboardButton("❌ 𝑵𝒐", callback_data="cnf|cancel|0")]])
    await update.message.reply_text(f"⚠️ {text}", reply_markup=kb, parse_mode=ParseMode.HTML)

async def confirm_handler(update, context):
    q = update.callback_query
    if not is_sudo(q.from_user.id): return await q.answer("❌ Not for you!", show_alert=True)
    data = q.data.split("|")
    act, arg = data[1], data[2]
    if act == "cancel": return await q.message.edit_text("❌ 𝑨𝒄𝒕𝒊𝒐𝒏 𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅.")

    try:
        if act == "addcoins":
            users_collection.update_one({"user_id": int(arg)}, {"$inc": {"balance": int(data[3])}})
            await q.message.edit_text(f"✅ 𝑪𝒐𝒊𝒏𝒔 𝑨𝒅𝒅𝒆𝒅 𝒕𝒐 {arg}")
        elif act == "rmcoins":
            users_collection.update_one({"user_id": int(arg)}, {"$inc": {"balance": -int(data[3])}})
            await q.message.edit_text(f"🗑️ 𝑪𝒐𝒊𝒏𝒔 𝑹𝒆𝒎𝒐𝒗𝒆𝒅 𝒇𝒓𝒐𝒎 {arg}")
        elif act == "freerevive":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"status": "alive", "death_time": None}})
            await q.message.edit_text(f"✨ 𝑼𝒔𝒆𝒓 {arg} 𝑹𝒆𝒗𝒊𝒗𝒆𝒅!")
        elif act == "unprotect":
            users_collection.update_one({"user_id": int(arg)}, {"$set": {"protection_expiry": datetime.utcnow()}})
            await q.message.edit_text(f"🛡️ 𝑺𝒉𝒊𝒆𝒍𝒅 𝑹𝒆𝒎𝒐𝒗𝒆𝒅 𝒇𝒐𝒓 {arg}")
    except Exception as e: await q.message.edit_text(f"❌ 𝑬𝒓𝒓𝒐𝒓: {e}")
