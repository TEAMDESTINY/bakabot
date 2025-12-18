# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Fixed Admin Plugin - Destiny / Baka Bot

import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID
from baka.utils import SUDO_USERS, get_mention, resolve_target, format_money, reload_sudoers, stylize_text
from baka.database import (
    users_collection, sudoers_collection, groups_collection, 
    reset_daily_activity, reset_weekly_activity
)

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
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id): return
    if len(context.args) < 1: 
        return await update.message.reply_text("⚠️ 𝑼𝒔𝒂𝒈𝒆: <code>/addcoins 100 @user</code>", parse_mode=ParseMode.HTML)
    
    amount, target_str = parse_amount_and_target(context.args)
    if amount <= 0:
        return await update.message.reply_text("❌ Sahi amount likho!")

    target, err = await resolve_target(update, context, specific_arg=target_str)
    if not target:
        return await update.message.reply_text(err or "❌ User nahi mila!")
    
    user_id = target['user_id']
    await ask(update, f"𝑨𝒅𝒅 {format_money(amount)} 𝒕𝒐 {get_mention(target)}?", "addcoins", f"{user_id}:{amount}")

async def rmcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id): return
    if len(context.args) < 1: 
        return await update.message.reply_text("⚠️ 𝑼𝒔𝒂𝒈𝒆: <code>/rmcoins 100 @user</code>", parse_mode=ParseMode.HTML)
    
    amount, target_str = parse_amount_and_target(context.args)
    if amount <= 0:
        return await update.message.reply_text("❌ Sahi amount likho!")

    target, err = await resolve_target(update, context, specific_arg=target_str)
    if not target:
        return await update.message.reply_text(err or "❌ User nahi mila!")
    
    user_id = target['user_id']
    await ask(update, f"𝑹𝒆𝒎𝒐ᴠ𝒆 {format_money(amount)} 𝒇𝒓𝒐𝒎 {get_mention(target)}?", "rmcoins", f"{user_id}:{amount}")

# --- SUDO MANAGEMENT ---
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: 
        return await update.message.reply_text("❌ Sirf Owner hi sudoers add kar sakta hai!")
    
    target, err = await resolve_target(update, context)
    if not target:
        return await update.message.reply_text(err or "⚠️ Reply to a user or provide username/ID.")
    
    await ask(update, f"𝑷𝒓𝒐𝒎𝒐𝒕𝒆 {get_mention(target)} 𝒕𝒐 𝑺𝒖𝒅𝒐?", "addsudo", str(target['user_id']))

# --- UTILS ---
def parse_amount_and_target(args):
    amount = 0
    target = None
    for arg in args:
        if arg.isdigit():
            amount = int(arg)
        else:
            target = arg
    return amount, target

async def ask(update: Update, text: str, act: str, arg: str):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ 𝒀𝒆𝒔", callback_data=f"cnf|{act}|{arg}"), 
        InlineKeyboardButton("❌ 𝑵𝒐", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ {text}", reply_markup=kb, parse_mode=ParseMode.HTML)

# --- CALLBACK HANDLER ---
async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not is_sudo(q.from_user.id): 
        return await q.answer("❌ Aapke liye nahi hai!", show_alert=True)
    
    data = q.data.split("|")
    act, arg = data[1], data[2]
    
    if act == "cancel": 
        return await q.message.edit_text("❌ 𝑨𝒄𝒕𝒊𝒐𝒏 𝑪𝒂𝒏𝒄𝒆𝒍𝒍𝒆𝒅.")

    try:
        if act in ["addcoins", "rmcoins"]:
            uid, amt = map(int, arg.split(":"))
            change = amt if act == "addcoins" else -amt
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": change}})
            await q.message.edit_text(f"✅ 𝑩𝒂𝒍𝒂𝒏𝒄𝒆 𝑼𝒑𝒅𝒂𝒕𝒆𝒅 for <code>{uid}</code>!", parse_mode=ParseMode.HTML)

        elif act == "addsudo":
            sudoers_collection.update_one({"user_id": int(arg)}, {"$set": {"user_id": int(arg)}}, upsert=True)
            reload_sudoers()
            await q.message.edit_text(f"✅ 𝑺𝒖𝒅𝒐 𝑷𝒓𝒐𝒎𝒐𝒕𝒆𝒅: <code>{arg}</code>", parse_mode=ParseMode.HTML)
            
    except Exception as e: 
        await q.message.edit_text(f"❌ 𝑬𝒓𝒓𝒐𝒓: {e}")
