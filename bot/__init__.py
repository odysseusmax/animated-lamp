from config import Config
from .main import get_bot_client, get_user_client
from .database import Database


bot = get_bot_client()
user = get_user_client()
db = Database(Config.DATABASE_URL)
CURRENT_PROCESSES = {}


async def run_bot():
    await user.start()
    await bot.start()
    
    await bot.idle()
    
    await bot.stop()
    await user.stop()
