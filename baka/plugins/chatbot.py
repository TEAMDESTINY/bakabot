# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final BAKA Chatbot - Full Sticker Links + Short Replies + Nezuko Style

import httpx
import random
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction, ChatType
from baka.config import MISTRAL_API_KEY, GROQ_API_KEY, CODESTRAL_API_KEY, BOT_NAME
from baka.database import chatbot_collection

# --- 🎨 NEZUKO FONT HELPER ---
def nezuko_style(text):
    """Converts text to Small Caps and Monospace for BAKA output."""
    lowered = str(text).lower()
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    small_caps = lowered.translate(mapping)
    return f"<code>{small_caps}</code>"

# --- 🎭 baka PERSONALITY CONFIG ---
BAKA_NAME = "BAKA"
EMOJI_POOL = ["✨", "💖", "🌸", "😊", "🥰", "💕", "🎀", "🌺", "💫", "🦋", "🌼", "💗", "🎨", "🍓", "🌟", "💝"]

MODELS = {
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama3-70b-8192", "key": GROQ_API_KEY},
    "mistral": {"url": "https://api.mistral.ai/v1/chat/completions", "model": "mistral-large-latest", "key": MISTRAL_API_KEY},
    "codestral": {"url": "https://codestral.mistral.ai/v1/chat/completions", "model": "codestral-latest", "key": CODESTRAL_API_KEY}
}

MAX_HISTORY = 8
DEFAULT_MODEL = "mistral"

# --- 🎭 FULL STICKER LINKS (RESTORED) ---
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
    "https://t.me/addstickers/cybercats_stickers"
]

FALLBACK_RESPONSES = ["ᴀᴄʜʜᴀ ᴊɪ? 😊", "ʜᴍᴍ... ᴀᴜʀ ʙᴀᴛᴀᴏ?", "ᴏᴋᴋ ᴏᴋᴋ! ✨", "sᴀʜɪ ʜᴀɪ ʏᴀᴀʀ 💖"]

# --- 📨 HELPER: SEND STICKER (LINK BASED) ---
async def send_ai_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tries to send a random sticker from configured packs."""
    try:
        raw_link = random.choice(STICKER_PACKS)
        pack_name = raw_link.replace("https://t.me/addstickers/", "")
        sticker_set = await context.bot.get_sticker_set(pack_name)
        if sticker_set and sticker_set.stickers:
            await update.message.reply_sticker(random.choice(sticker_set.stickers).file_id)
    except: pass

# --- 🧠 AI CORE ENGINE ---
async def call_model_api(provider, messages, max_tokens):
    conf = MODELS.get(provider)
    if not conf or not conf["key"]: return None
    headers = {"Authorization": f"Bearer {conf['key']}", "Content-Type": "application/json"}
    payload = {"model": conf["model"], "messages": messages, "temperature": 0.8, "max_tokens": max_tokens}
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(conf["url"], json=payload, headers=headers)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except: return None

async def get_ai_response(chat_id, user_input, user_name, selected_model=DEFAULT_MODEL):
    is_code = any(kw in user_input.lower() for kw in ["code", "python", "html", "fix", "debug", "import"])
    active_model = "codestral" if is_code else selected_model
    
    # 📏 Strict Limit for Short Replies
    max_tokens = 4096 if is_code else 60 

    system_prompt = (
        f"You are {BAKA_NAME}, a sweet Hinglish AI girlfriend. "
        f"STRICT RULE: Reply in only 1-2 SHORT sentences. No long text. "
        f"Match user energy. User: {user_name}"
    )

    doc = chatbot_collection.find_one({"chat_id": chat_id}) or {}
    history = doc.get("history", [])
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-MAX_HISTORY:]: messages.append(msg)
    messages.append({"role": "user", "content": user_input})

    reply = await call_model_api(active_model, messages, max_tokens)
    if not reply: reply = random.choice(FALLBACK_RESPONSES)

    new_history = history + [{"role": "user", "content": user_input}, {"role": "assistant", "content": reply}]
    chatbot_collection.update_one({"chat_id": chat_id}, {"$set": {"history": new_history[-16:]}}, upsert=True)

    return reply, is_code

# --- 💬 MESSAGE HANDLER ---
async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg: return
    chat = update.effective_chat

    # Sticker logic
    if msg.sticker:
        if chat.type == ChatType.PRIVATE or (msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id):
            await send_ai_sticker(update, context)
        return

    if not msg.text or msg.text.startswith("/"): return

    should_reply = (chat.type == ChatType.PRIVATE or 
                    (msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id) or
                    any(msg.text.lower().startswith(kw) for kw in ["hey", "hi", "baka", "oye", "sun"]))

    if should_reply:
        await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
        doc = chatbot_collection.find_one({"chat_id": chat.id})
        pref_model = doc.get("model", DEFAULT_MODEL) if doc else DEFAULT_MODEL
        
        response, is_code = await get_ai_response(chat.id, msg.text, msg.from_user.first_name, pref_model)

        if is_code:
            await msg.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text(nezuko_style(response), parse_mode=ParseMode.HTML)
            if random.random() < 0.20: await send_ai_sticker(update, context)

# --- 🔧 COMMAND: /ask ---
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(nezuko_style("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ǫᴜᴇsᴛɪᴏɴ !"), parse_mode=ParseMode.HTML)
    query = " ".join(context.args)
    response, is_code = await get_ai_response(update.effective_chat.id, query, update.effective_user.first_name)
    if is_code:
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(nezuko_style(response), parse_mode=ParseMode.HTML)
