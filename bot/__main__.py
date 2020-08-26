import logging

from .screenshotbot import ScreenShotBot
from .config import Config

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG if Config.DEBUG else logging.INFO)
    logging.getLogger("pyrogram").setLevel(logging.INFO if Config.DEBUG else logging.WARNING)
    
    ScreenShotBot().run()
