# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL MASTER RYAN.PY - MONOSPACE ROSE MENU & MULTI-HANDLER SYNC
# Added PrefixHandler for .help support

import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ChatMemberHandler, filters, PrefixHandler
)
from telegram.request import HTTPXRequest

# Error noise control
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- INTERNAL IMPORTS ---
try:
    from baka.config import TOKEN, PORT
    from baka.utils import BOT_NAME
    from baka.plugins import (
        start, economy, game, admin, broadcast, fun, events, 
        ping, chatbot, riddle, waifu, shop, couple, bomb, welcome
    )
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    exit(1)

# --- FLASK SERVER (Uptime Monitoring) ---
app = Flask(__name__)
@app.route('/')
def health(): return "Destiny Engine Active! 🚀"

def run_flask(): 
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# --- 🌹 STYLIZED STARTUP MENU SYNC ---
async def post_init(application):
    """Syncs the stylized command list to the bot menu button."""
    commands = [
        ("start", "🌹 𝚂𝚝𝚊𝚛𝚝 𝙼𝚊𝚒𝚗 𝙼𝚎𝚗𝚞"), 
        ("help", "🌹 𝙷𝚎𝚕𝚙 𝙶𝚞𝚒𝚍𝚎 𝙳𝚒𝚊𝚛𝚢"),
        ("bal", "🌹 𝚆𝚊𝚕𝚕𝚎𝚝 𝙱𝚊𝚕𝚊𝚗𝚌𝚎"), 
        ("toprich", "🌹 𝚁𝚒𝚌𝚑 𝙻𝚎𝚊𝚍𝚎𝚛𝚋𝚘𝚊𝚛𝚍"), 
        ("topkill", "🌹 𝙺𝚒𝚕𝚕 𝙻𝚎𝚊𝚍𝚎𝚛𝚋𝚘𝚊𝚛𝚍"),
        ("daily", "🌹 𝙲𝚕𝚊𝚒𝚖 $𝟷𝟶𝟶𝟶 (𝙳𝚖 𝙾𝚗𝚕𝚢)"),
        ("bomb", "🌹 𝚂𝚝𝚊𝚛𝚝 𝙱𝚘𝚖𝚋 𝙶𝚊𝚖𝚎"),
        ("leaders", "🌹 𝙱𝚘𝚖𝚋 𝙶𝚊𝚖𝚎 𝚁𝚊𝚗𝚔𝚒𝚗𝚐𝚜"),
        ("claim", "🌹 𝙶𝚛𝚘𝚞𝚙 𝚁𝚎𝚠𝚊𝚛𝚍 𝙲𝚕𝚊𝚒𝚖"),
        ("kill", "🌹 𝙺𝚒𝚕𝚕 𝚂𝚘𝚖𝚎𝚘𝚗𝚎"), 
        ("rob", "🌹 𝚂𝚝𝚎𝚊𝚕 𝙼𝚘𝚗𝚎𝚢 (𝙻𝚒𝚖𝚒𝚝)"),
        ("items", "🌹 𝙶𝚒𝚏𝚝 𝚂𝚑𝚘𝚙 𝙸𝚝𝚎𝚖𝚜"),
        ("item", "🌹 𝙼𝚢 𝙸𝚗𝚟𝚎𝚗𝚝𝚘𝚛𝚢"),
        ("myrank", "🌹 𝙶𝚕𝚘𝚋𝚊𝚕 𝚁𝚊𝚗𝚔 𝚂𝚝𝚊𝚝𝚜"),
        ("economy", "🌹 𝙴𝚌𝚘𝚗𝚘𝚖𝚢 𝙶𝚞𝚒𝚍𝚎 𝙱𝚘𝚘𝚔")
    ]
    await application.bot.set_my_commands(commands)
    print(f"✅ {BOT_NAME} Rose-Styled Menu Synchronized!")

# --- MAIN ENGINE ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        # Optimizing connection for high traffic
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # 1. 🌹 Core & Welcome Handlers
        app_bot.add_handler(CommandHandler("start", start.start))
        
        # ✅ CHANGED: PrefixHandler for .help and /help support
        app_bot.add_handler(PrefixHandler(["/", "."], "help", start.help_command))
        
        app_bot.add_handler(CommandHandler("welcome", welcome.welcome_command))
        
        # Note: Ensure start.py has help_callback function to avoid AttributeError
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_|return_start"))
        
        # New Member Welcome Message
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))

        # 2. 🔐 Admin & Sudo Registration
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CommandHandler("bombcancel", bomb.bomb_cancel)) 
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))

        # 3. 💰 Economy & Gifting System
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("daily", economy.daily_bonus)) 
        app_bot.add_handler(CommandHandler("toprich", economy.toprich))   
        app_bot.add_handler(CommandHandler("myrank", economy.my_rank))    
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("topkill", economy.top_kill))
        
        # Shop & Items
        app_bot.add_handler(CommandHandler("items", shop.items_list))   
        app_bot.add_handler(CommandHandler("item", shop.view_inventory)) 
        app_bot.add_handler(CommandHandler("gift", shop.gift_item))      

        # 4. ⚔️ Game & Combat
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob)) 
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))

        # 5. 💣 Bomb Game Integration
        app_bot.add_handler(CommandHandler("bomb", bomb.start_bomb))
        app_bot.add_handler(CommandHandler("join", bomb.join_bomb))
        app_bot.add_handler(CommandHandler("pass", bomb.pass_bomb))
        app_bot.add_handler(CommandHandler("leaders", bomb.bomb_leaders)) 
        app_bot.add_handler(CommandHandler("bombrank", bomb.bomb_myrank)) 

        # 6. 🧠 Chatbot, AI & Fun
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chatbot.ai_message_handler))
        app_bot.add_handler(CommandHandler("couple", couple.couple)) 
        app_bot.add_handler(CommandHandler("waifu", waifu.waifu_cmd)) 
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle))
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))

        # 7. 📊 Listeners & Logs (Events)
        app_bot.add_handler(CommandHandler("claim", events.claim_group))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        
        # Tracking Group Activity
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)
        
        # Master Log Handler (Join/Leave/Promote)
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))

        print(f"🚀 {BOT_NAME} MASTER ENGINE ONLINE!")
        app_bot.run_polling(drop_pending_updates=True)
