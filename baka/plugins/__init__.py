# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Plugins Initializer - Circular Import Fixed

# Sabhi plugins ki list define karein
__all__ = [
    "start",
    "economy",
    "game",
    "admin",
    "broadcast",
    "fun",
    "events",
    "welcome",
    "ping",
    "chatbot",
    "riddle",
    "waifu",
    "shop",
    "couple",
    "flash_event",
    "bomb"
]

# Explicit imports taaki circular dependency na ho
from . import start, economy, game, admin, broadcast, fun, events, welcome, ping, chatbot, riddle, waifu, shop, couple, flash_event, bomb
