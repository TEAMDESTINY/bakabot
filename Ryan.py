
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
        ping, chatbot, riddle, waifu, shop, couple, bomb, welcome,
        flash_event  #
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
    """Syncs the command list to the bot menu button with custom 𝐒ᴛʏʟɪᴢᴇᴅ font."""
    commands = [
        ("start", "𝐒ᴛᴀʀᴛ ᴛʜᴇ 𝐒ʏꜱᴛᴇᴍ 🌹"), 
        ("help", "𝐇ᴇʟ𝐩 𝐆ᴜɪᴅᴇ 𝐃ɪᴀʀ𝐲 🌹"),
        ("bal", "𝐖ᴀ𝐋ʟᴇᴛ 𝐁ᴀ𝐋ᴀɴᴄᴇ 🌹"), 
        ("toprich", "𝐑ɪ𝐂𝐡 𝐋ᴇᴀ𝐃ᴇʀ𝐁𝐨𝐚𝐑𝐝 🌹"), 
        ("topkill", "𝐊ɪ𝐋ʟ 𝐋ᴇᴀ𝐃ᴇʀ𝐁𝐨𝐚𝐑𝐝 🌹"),
        ("daily", "𝐂ʟᴀɪᴍ 𝐃ᴀɪ𝐋ʏ 𝐑ᴇ𝐖ᴀ𝐑𝐝 🌹"),
        ("bomb", "𝐒ᴛᴀ𝐑ᴛ 𝐁𝐨𝐌𝐛 𝐆ᴀ𝐌ᴇ 🌹"),
        ("leaders", "𝐁𝐨𝐌𝐛 𝐆ᴀ𝐌ᴇ 𝐑ᴀɴ𝐊𝐢ɴ𝐆𝐬 🌹"),
        ("claim", "𝐆𝐫𝐨𝐔𝐩 𝐑ᴇ𝐖ᴀ𝐑𝐝 𝐂ʟᴀ𝐈𝐦 🌹"),
        ("kill", "𝐊ɪ𝐋ʟ 𝐒𝐨𝐌ᴇ𝐨𝐍ᴇ 🌹"), 
        ("rob", "𝐒ᴛᴇᴀ𝐋 𝐌𝐨𝐍ᴇ𝐘 🌹"),
        ("items", "𝐆ɪ𝐅𝐭 𝐒𝐡𝐎𝐩 𝐈ᴛᴇ𝐌𝐬 🌹"),
        ("item", "𝐌ʏ 𝐈ɴ𝐕ᴇ𝐍ᴛ𝐨𝐑𝐲 🌹"),
        ("myrank", "𝐆𝐥𝐎𝐛𝐀𝐥 𝐑ᴀɴ𝐊 𝐒ᴛᴀ𝐓𝐬 🌹"),
        ("economy", "𝐄𝐜𝐎ɴ𝐨𝐌ʏ 𝐆ᴜ𝐈𝐝𝐄 𝐁𝐨𝐎𝐤 🌹"),
        ("collect", "𝐅𝐥𝐀𝐬𝐇 𝐂𝐨𝐋ʟᴇ𝐂𝐭 𝐄𝐯𝐄ɴᴛ 🌹") #
    ]
    await application.bot.set_my_commands(commands)
    print(f"✅ {BOT_NAME} Stylized Command Menu Synchronized!") #

# --- MAIN ENGINE ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    if not TOKEN:
        print("CRITICAL: TOKEN MISSING!")
    else:
        # Optimizing connection for high traffic
        t_request = HTTPXRequest(connection_pool_size=30, read_timeout=40.0)
        app_bot = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()

        # 1. 🌹 Core Handlers
        app_bot.add_handler(CommandHandler("start", start.start))
        app_bot.add_handler(PrefixHandler(["/", "."], "help", start.help_command)) #
        app_bot.add_handler(CommandHandler("game", start.game_guide))
        app_bot.add_handler(CommandHandler("economy", start.economy_guide))
        
        # Callback Handlers
        app_bot.add_handler(CallbackQueryHandler(start.start_callback, pattern="^(talk_baka|game_features|return_start)$"))
        app_bot.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_"))
        
        app_bot.add_handler(CommandHandler("welcome", welcome.welcome_command))
        app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.new_member))

        # 2. 🔐 Admin & Sudo Registration
        app_bot.add_handler(CommandHandler("sudo", admin.sudo_help))
        app_bot.add_handler(CommandHandler("addcoins", admin.addcoins))
        app_bot.add_handler(CommandHandler("rmcoins", admin.rmcoins))
        app_bot.add_handler(CommandHandler("freerevive", admin.freerevive))
        app_bot.add_handler(CommandHandler("unprotect", admin.unprotect))
        app_bot.add_handler(CommandHandler("broadcast", broadcast.broadcast))
        app_bot.add_handler(CommandHandler("bombcancel", bomb.bomb_cancel)) 
        app_bot.add_handler(CommandHandler("setflash", flash_event.set_flash)) #
        app_bot.add_handler(CallbackQueryHandler(admin.confirm_handler, pattern=r"^cnf\|"))

        # 3. 💰 Economy System
        app_bot.add_handler(CommandHandler("bal", economy.balance))
        app_bot.add_handler(CommandHandler("daily", economy.daily_bonus)) #
        app_bot.add_handler(CommandHandler("toprich", economy.toprich))   
        app_bot.add_handler(CommandHandler("myrank", economy.my_rank))    
        app_bot.add_handler(CommandHandler("give", economy.give))
        app_bot.add_handler(CommandHandler("topkill", economy.top_kill))
        
        # Shop
        app_bot.add_handler(CommandHandler("items", shop.items_list))   
        app_bot.add_handler(CommandHandler("item", shop.view_inventory)) 
        app_bot.add_handler(CommandHandler("gift", shop.gift_item))      

        # 4. ⚔️ Game & Combat
        app_bot.add_handler(CommandHandler("kill", game.kill))
        app_bot.add_handler(CommandHandler("rob", game.rob)) #
        app_bot.add_handler(CommandHandler("revive", game.revive))
        app_bot.add_handler(CommandHandler("protect", game.protect))

        # 5. 💣 Bomb Game Logic
        app_bot.add_handler(CommandHandler("bomb", bomb.start_bomb))
        app_bot.add_handler(CommandHandler("join", bomb.join_bomb))
        app_bot.add_handler(CommandHandler("pass", bomb.pass_bomb))
        app_bot.add_handler(CommandHandler("leaders", bomb.bomb_leaders)) 
        app_bot.add_handler(CommandHandler("bombrank", bomb.bomb_myrank)) 

        # 6. 🧠 AI & Flash Event
        app_bot.add_handler(CommandHandler("ask", chatbot.ask_ai))
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chatbot.ai_message_handler))
        app_bot.add_handler(CommandHandler("collect", flash_event.collect)) #
        app_bot.add_handler(CommandHandler("couple", couple.couple)) 
        app_bot.add_handler(CommandHandler("waifu", waifu.waifu_cmd)) 
        app_bot.add_handler(CommandHandler("riddle", riddle.riddle))
        app_bot.add_handler(CommandHandler("dice", fun.dice))
        app_bot.add_handler(CommandHandler("slots", fun.slots))

        # 7. 📈 Listeners & Economy Toggles
        app_bot.add_handler(CommandHandler("claim", events.claim_group))
        app_bot.add_handler(CommandHandler("ping", ping.ping))
        
        # Economy Enable/Disable
        app_bot.add_handler(CommandHandler("open", events.open_economy)) #
        app_bot.add_handler(CommandHandler("close", events.close_economy)) #
        
        # Tracking & Logs
        app_bot.add_handler(MessageHandler(filters.ChatType.GROUPS, events.group_tracker), group=3)
        app_bot.add_handler(ChatMemberHandler(events.chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))

        print(f"🚀 {BOT_NAME} MASTER ENGINE ONLINE!")
        app_bot.run_polling(drop_pending_updates=True)
