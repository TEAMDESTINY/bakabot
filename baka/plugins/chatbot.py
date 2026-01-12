# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar
#
# All rights reserved.

import httpx
import random
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction, ChatType
from telegram.error import BadRequest

from baka.config import (
    MISTRAL_API_KEY,
    GROQ_API_KEY,
    CODESTRAL_API_KEY,
    BOT_NAME,
    OWNER_LINK,
)
from baka.database import chatbot_collection
from baka.utils import stylize_text

# --- BAKA CONFIG ---
BAKA_NAME = "BAKA"

EMOJI_POOL = [
    "✨", "💖", "🌸", "😊", "🥰", "💕", "🎀", "🌺",
    "💫", "🦋", "🌼", "💗", "🎨", "🍓", "☺️",
    "😌", "🌟", "💝"
]

# --- MODEL SETTINGS ---
MODELS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama3-70b-8192",
        "key": GROQ_API_KEY,
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-large-latest",
        "key": MISTRAL_API_KEY,
    },
    "codestral": {
        "url": "https://codestral.mistral.ai/v1/chat/completions",
        "model": "codestral-latest",
        "key": CODESTRAL_API_KEY,
    },
}

MAX_HISTORY = 8
DEFAULT_MODEL = "mistral"

# --- STICKERS ---
STICKER_PACKS = [
    "https://t.me/addstickers/RandomByDarkzenitsu",
    "https://t.me/addstickers/Null_x_sticker_2",
    "https://t.me/addstickers/pack_73bc9_by_TgEmojis_bot",
    "https://t.me/addstickers/animation_0_8_Cat",
    "https://t.me/addstickers/vhelw_by_CalsiBot",
    "https://t.me/addstickers/Rohan_yad4v1745993687601_by_toWebmBot",
    "https://t.me/addstickers/MySet199",
    "https://t.me/addstickers/Quby741",
    "https://t.me/addstickers/Animalsasthegtjtky_by_fStikBot",
    "https://t.me/addstickers/a6962237343_by_Marin_Roxbot",
    "https://t.me/addstickers/cybercats_stickers",
]

FALLBACK_RESPONSES = [
    "Achha ji?",
    "Hmm... aur batao?",
    "Okk okk!",
    "Sahi hai yaar",
    "Toh phir?",
    "Interesting!",
    "Aur kya chal raha?",
    "Sunao sunao!",
    "Haan haan",
    "Theek hai",
]

# --- STICKER SENDER ---
async def send_ai_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        link = random.choice(STICKER_PACKS)
        pack = link.replace("https://t.me/addstickers/", "")
        sticker_set = await context.bot.get_sticker_set(pack)
        if sticker_set.stickers:
            sticker = random.choice(sticker_set.stickers)
            await update.message.reply_sticker(sticker.file_id)
    except Exception:
        pass

# --- API CALL ---
async def call_model_api(provider, messages, max_tokens):
    conf = MODELS.get(provider)
    if not conf or not conf["key"]:
        return None

    headers = {
        "Authorization": f"Bearer {conf['key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": conf["model"],
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": max_tokens,
        "top_p": 0.9,
    }

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.post(conf["url"], json=payload, headers=headers)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[AI ERROR] {provider}: {e}")

    return None

# --- CORE AI ---
async def get_ai_response(chat_id, user_input, user_name, selected_model=DEFAULT_MODEL):
    code_keywords = [
        "code", "python", "html", "css", "javascript",
        "error", "fix", "debug", "script", "program"
    ]

    is_code = any(k in user_input.lower() for k in code_keywords)
    active_model = "codestral" if is_code else selected_model
    max_tokens = 4096 if is_code else 200

    system_prompt = (
        "You are a helpful assistant."
        if is_code else
        "You are BAKA, a sweet Indian Hinglish chatbot."
    )

    doc = chatbot_collection.find_one({"chat_id": chat_id}) or {}
    history = doc.get("history", [])

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": user_input})

    reply = await call_model_api(active_model, messages, max_tokens)

    if not reply:
        reply = random.choice(FALLBACK_RESPONSES)

    reply = reply.replace("*", "").strip()

    new_history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": reply},
    ]

    chatbot_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"history": new_history[-MAX_HISTORY * 2:]}},
        upsert=True,
    )

    return reply, is_code

# --- MESSAGE HANDLER ---
async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    await context.bot.send_chat_action(msg.chat.id, ChatAction.TYPING)

    doc = chatbot_collection.find_one({"chat_id": msg.chat.id}) or {}
    model = doc.get("model", DEFAULT_MODEL)

    reply, is_code = await get_ai_response(
        msg.chat.id,
        msg.text.strip(),
        msg.from_user.first_name,
        model,
    )

    if is_code:
        await msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
    else:
        await msg.reply_text(stylize_text(reply))

    if random.random() < 0.2:
        await send_ai_sticker(update, context)
