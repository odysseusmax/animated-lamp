import pyrogram

from config import Config


def get_bot_client():
    plugins = dict(
        root="bot/plugins"
    )
    bot = pyrogram.Client(
        Config.SESSION_NAME,
        bot_token = Config.BOT_TOKEN,
        api_id = Config.API_ID,
        api_hash = Config.API_HASH,
        workers = 20,
        plugins = plugins
    )
    return bot
