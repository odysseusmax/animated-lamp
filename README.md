# [Screenshotit_bot](https://tx.me/screenshotit_bot)
> Telegram Bot For Screenshot Generation

## Description

An attempt to implement the screenshot generation of telegram files without downloading the entire file. Live version can be found here [@screenshotit_bot](https://tx.me/screenshotit_bot "Screenshot Generator Bot")

## Installation Guide

### Prerequisites
* FFmpeg
* Python3 (3.8.2)

### Local setup
* Clone to local machine.
```
$ git clone https://github.com/odysseusmax/animated-lamp.git
$ cd animated-lamp
````

* Create virtualenv
```
$ pip3 install virtualenv
$ virtualenv venv
$ source venv/bin/activate
```

* Install dependencies
```
$ pip3 install -r requirements.txt
```

### Environment Variables
Properly setup the environment variables.
* `API_ID`(required) - Get your telegram API_ID from [https://my.telegram.org/](https://my.telegram.org/)
* `API_HASH`(required) - Get your telegram API_HASH from [https://my.telegram.org/](https://my.telegram.org/)
* `BOT_TOKEN`(required) - Obtain your bot token from [Bot Father](https://t.me/BotFather "Bot Father")
* `SESSION_NAME`(required) - Name you want to call your bot's session, Eg: bot username
* `USER_SESSION_STRING`(required) - Userbot's session string.
* `MIDDLE_MAN`(required) - Middle man channel's id.
* `LINK_GEN_BOT`(required) - Username of the bot that generates streamable links for the telegram files.
* `LOG_CHANNEL`(required) Log channel's id.
* `DATABASE_URL`(required) - Mongodb database URI
* `AUTH_USERS`(required) - Authorised user(s) id separated by space.

### Run bot
`$ python3 run.py`

Now go to your bot and do a /start.

## Contributions
Contributions are welcome.

## Contact
You can contact me [@odysseusmax](https://tx.me/odysseusmax)

## Thanks
Thanks to [Dan](https://github.com/delivrance) for his [Pyrogram](https://github.com/pyrogram/pyrogram "Pyrogram") library.

## License
Code released under [The GNU General Public License](LICENSE).
