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


def get_user_client():
    user = pyrogram.Client(
        Config.USER_SESSION_STRING,
        api_id = Config.API_ID,
        api_hash = Config.API_HASH,
    )
    return user
