from .main import get_bot_client, get_user_client


bot = get_bot_client()
user = get_user_client()


async def run_bot():
    await user.start()
    await bot.start()
    
    await bot.idle()
    
    await bot.stop()
    await user.stop()
