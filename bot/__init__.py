from config import Config
from .main import get_bot_client
from .database import Database


bot = get_bot_client()
db = Database(Config.DATABASE_URL)
CURRENT_PROCESSES = {}
CHAT_FLOOD = {}


async def run_bot():
    await bot.start()
    
    await bot.idle()
    
    await bot.stop()
