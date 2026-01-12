# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Short Chatbot - Strictly One Line Responses

import httpx
import random
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction, ChatType
from telegram.error import BadRequest
from baka.config import MISTRAL_API_KEY, GROQ_API_KEY, CODESTRAL_API_KEY, BOT_NAME, OWNER_LINK
from baka.database import chatbot_collection
from baka.utils import stylize_text 

# --- 🎨 BAKA PERSONALITY CONFIG ---
BAKA_NAME = "BAKA"
EMOJI_POOL = ["✨", "💖", "🌸", "😊", "🥰", "💕", "🎀", "🌺", "💫", "🦋", "🌼", "💗", "🎨", "🍓", "☺️", "😌", "🌟", "💝"]

# --- 🤖 MODEL SETTINGS ---
MODELS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama3-70b-8192",
        "key": GROQ_API_KEY
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-large-latest",
        "key": MISTRAL_API_KEY
    },
    "codestral": {
        "url": "https://codestral.mistral.ai/v1/chat/completions",
        "model": "codestral-latest",
        "key": CODESTRAL_API_KEY
    }
}

MAX_HISTORY = 5  # Reduced history for focus
DEFAULT_MODEL = "mistral"

# --- 🎭 STICKER PACKS ---
STICKER_PACKS = [
    "https://t.me/addstickers/RandomByDarkzenitsu",
    "https://t.me/addstickers/Null_x_sticker_2",
    "https://t.me/addstickers/pack_73bc9_by_TgEmojis_bot",
    "https://t.me/addstickers/animation_0_8_Cat",
    "https://t.me/addstickers/vhelw_by_CalsiBot",
    "https://t.me/addstickers/cybercats_stickers"
]

FALLBACK_RESPONSES = ["Achha ji? 😊", "Okk okk! ✨", "Sahi hai yaar 💖", "Theek hai 🥰"]

# --- 📨 HELPER: SEND STICKER ---
async def send_ai_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw_link = random.choice(STICKER_PACKS)
        pack_name = raw_link.replace("https://t.me/addstickers/", "")
        sticker_set = await context.bot.get_sticker_set(pack_name)
        if sticker_set and sticker_set.stickers:
            sticker = random.choice(sticker_set.stickers)
            await update.message.reply_sticker(sticker.file_id)
    except: pass

# --- 🧠 AI CORE ENGINE ---

async def call_model_api(provider, messages, max_tokens):
    conf = MODELS.get(provider)
    if not conf or not conf["key"]: return None
    headers = {"Authorization": f"Bearer {conf['key']}", "Content-Type": "application/json"}
    payload = {"model": conf["model"], "messages": messages, "temperature": 0.7, "max_tokens": max_tokens}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(conf["url"], json=payload, headers=headers)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except: pass
    return None

async def get_ai_response(chat_id: int, user_input: str, user_name: str, selected_model=DEFAULT_MODEL):
    # --- 1️⃣ CODE DETECTION ---
    code_keywords = ["code", "python", "html", "css", "javascript", "script", "function", "fix"]
    is_coding_request = any(kw in user_input.lower() for kw in code_keywords)

    if is_coding_request:
        active_model = "codestral"
        max_tokens = 1000
        system_prompt = "You are a coding assistant. Provide clean, short, working code."
    else:
        active_model = selected_model
        # 📏 STRICT LIMIT: Only 35 tokens for short replies
        max_tokens = 35 
        
        # 💕 Baka Persona (Strictly One-Line Hinglish)
        system_prompt = (
            f"You are {BAKA_NAME}, a sweet Indian girlfriend. Speak natural Hinglish.\n"
            "STRICT RULES:\n"
            "1. Respond in ONLY ONE short, sassy sentence.\n"
            "2. Max 10-12 words only. Be very brief.\n"
            "3. Use simple Hindi+English mix. NO asterisks (*smiles*).\n"
            "4. Match the user's energy but keep it snappy."
        )

    # --- 2️⃣ BUILD CONTEXT ---
    doc = chatbot_collection.find_one({"chat_id": chat_id}) or {}
    history = doc.get("history", [])
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-MAX_HISTORY:]: messages.append(msg)
    messages.append({"role": "user", "content": user_input})

    # --- 3️⃣ GENERATION ---
    reply = await call_model_api(active_model, messages, max_tokens)
    if not reply: reply = await call_model_api("mistral", messages, max_tokens)
    if not reply: return random.choice(FALLBACK_RESPONSES), is_coding_request

    # --- 4️⃣ CLEANUP (Force Single Line) ---
    # Sirf pehli line rakhega aur faaltu characters hatayega
    reply = reply.split('\n')[0].replace('*', '').strip() 

    # --- 5️⃣ SAVE MEMORY ---
    new_history = history + [{"role": "user", "content": user_input}, {"role": "assistant", "content": reply}]
    chatbot_collection.update_one({"chat_id": chat_id}, {"$set": {"history": new_history[-10:]}}, upsert=True)

    return reply, is_coding_request

# --- ⚙️ SETTINGS MENU & HANDLERS ---
# (Same as your provided code, no changes needed for Menu/Callbacks)
async def chatbot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == ChatType.PRIVATE:
        doc = chatbot_collection.find_one({"chat_id": chat.id})
        curr_model = doc.get("model", DEFAULT_MODEL) if doc else DEFAULT_MODEL
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🦙 Groq", callback_data="ai_set_groq"), InlineKeyboardButton("🌟 Mistral", callback_data="ai_set_mistral")],
            [InlineKeyboardButton("🖥️ Codestral", callback_data="ai_set_codestral")],
            [InlineKeyboardButton("🗑️ Clear Memory", callback_data="ai_reset")]
        ])
        return await update.message.reply_text(f"🤖 <b>Baka AI Settings</b>\n📍 Model: {curr_model.title()}", parse_mode=ParseMode.HTML, reply_markup=kb)

    # ... [Rest of chatbot_menu and chatbot_callback logic remains the same] ...

# --- 💬 MESSAGE HANDLER ---
async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"): return
    chat = update.effective_chat
    text = msg.text.strip()

    should_reply = False
    if chat.type == ChatType.PRIVATE: should_reply = True
    else:
        doc = chatbot_collection.find_one({"chat_id": chat.id})
        if doc and not doc.get("enabled", True): return
        bot_username = context.bot.username.lower()
        if (msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id) or \
           f"@{bot_username}" in text.lower() or \
           any(text.lower().startswith(kw) for kw in ["hey", "hi", "hello", "baka"]):
            should_reply = True
            text = text.replace(f"@{bot_username}", "").strip()

    if should_reply:
        await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
        doc = chatbot_collection.find_one({"chat_id": chat.id})
        pref_model = doc.get("model", DEFAULT_MODEL) if doc else DEFAULT_MODEL
        response, is_code = await get_ai_response(chat.id, text or "Hi", msg.from_user.first_name, pref_model)

        if is_code: await msg.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else: await msg.reply_text(stylize_text(response))

# --- 🔧 COMMAND: /ask ---
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("💬 Usage: /ask <question>")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    response, is_code = await get_ai_response(update.effective_chat.id, " ".join(context.args), update.effective_user.first_name, DEFAULT_MODEL)
    if is_code: await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else: await update.message.reply_text(stylize_text(response))
