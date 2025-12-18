# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Fixed Admin Plugin - Destiny / Baka Bot

import html
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, UPSTREAM_REPO, GIT_TOKEN
from baka.utils import SUDO_USERS, get_mention, resolve_target, format_money, reload_sudoers, stylize_text
from baka.database import users_collection, sudoers_collection, groups_collection

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
        f"<b>👑 {stylize_text('Owner Only')}:</b>\n"
        "‣ /update | /cleandb\n"
        "‣ /addsudo | /rmsudo\n"
        "‣ /sudolist"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- ECONOMY ACTIONS ---
async def addcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    amount, target_str = parse_amount_and_target(context.args)
    if amount is None: return await update.message.reply_text("⚠️ 𝑼𝒔𝒂𝒈𝒆: <code>/addcoins 100 @user</code>", parse_mode=ParseMode.HTML)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if not target: return await update.message.reply_text(err or "⚠️ Target not found.")
    
    await ask(update, f"Add {format_money(amount)} to {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")

async def rmcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    amount, target_str = parse_amount_and_target(context.args)
    if amount is None: return await update.message.reply_text("⚠️ 𝑼𝒔𝒂𝒈𝒆: <code>/rmcoins 100 @user</code>", parse_mode=ParseMode.HTML)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if not target: return await update.message.reply_text(err or "⚠️ Target not found.")
    
    await ask(update, f"Remove {format_money(amount)} from {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")

# --- SUDO & OWNER MANAGEMENT ---
async def addsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Promote {get_mention(target)} to Sudo?", "addsudo", str(target['user_id']))

async def rmsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Demote {get_mention(target)} from Sudo?", "rmsudo", str(target['user_id']))

async def sudolist(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    msg = f"👑 <b>{stylize_text('Owner & Sudoers')}:</b>\n\n"
    for uid in list(SUDO_USERS):
        u_doc = users_collection.find_one({"user_id": uid})
        role = "Owner" if uid == OWNER_ID else "Sudoer"
        msg += f"• {get_mention(u_doc) if u_doc else f'<code>{uid}</code>'} - {role}\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- SYSTEM COMMANDS ---
async def freerevive(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Free Revive {get_mention(target)}?", "freerevive", str(target['user_id']))

async def unprotect(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Remove shield from {get_mention(target)}?", "unprotect", str(target['user_id']))

async def cleandb(update, context):
    if update.effective_user.id != OWNER_ID: return
    await ask(update, "<b>WIPE DATABASE?</b> 🗑️", "cleandb", "0")

# --- UTILS ---
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

# --- CALLBACK CONFIRMATION ---
async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id not in SUDO_USERS: 
        return await q.answer("❌ Not for you!", show_alert=True)
    
    data = q.data.split("|")
    act = data[1]
    
    if act == "cancel": 
        return await q.message.edit_text("❌ <b>Action Cancelled.</b>", parse_mode=ParseMode.HTML)

    try:
        if act == "addcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text(f"✅ Added <b>{format_money(amt)}</b> to <code>{uid}</code>.", parse_mode=ParseMode.HTML)
            
        elif act == "rmcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
            await q.message.edit_text(f"🗑️ Removed <b>{format_money(amt)}</b> from <code>{uid}</code>.", parse_mode=ParseMode.HTML)

        elif act == "addsudo":
            uid = int(data[2])
            sudoers_collection.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
            reload_sudoers()
            await q.message.edit_text(f"✅ User <code>{uid}</code> promoted to Sudo.")

        elif act == "rmsudo":
            uid = int(data[2])
            sudoers_collection.delete_one({"user_id": uid})
            reload_sudoers()
            await q.message.edit_text(f"🗑️ User <code>{uid}</code> demoted from Sudo.")

        elif act == "freerevive":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"status": "alive", "death_time": None}})
            await q.message.edit_text(f"✨ User <code>{uid}</code> revived.")
            
        elif act == "unprotect":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"protection": None, "protection_expiry": None}})
            await q.message.edit_text(f"🛡️ Shield removed for <code>{uid}</code>.")

        elif act == "cleandb":
            users_collection.delete_many({})
            groups_collection.delete_many({})
            await q.message.edit_text("🗑️ <b>DATABASE WIPED!</b>")
            
    except Exception as e:
        await q.message.edit_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode=ParseMode.HTML)
