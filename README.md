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

* `API_ID`(required) - Get your telegram API_ID from [https://my.telegram.org/](https://my.telegram.org/).
* `API_HASH`(required) - Get your telegram API_HASH from [https://my.telegram.org/](https://my.telegram.org/).
* `BOT_TOKEN`(required) - Obtain your bot token from [Bot Father](https://t.me/BotFather "Bot Father").
* `SESSION_NAME`(required) - Name you want to call your bot's session, Eg: bot username.
* `USER_SESSION_STRING`(required) - Userbot's session string ([Generate Session String](https://generatesessionstring.christyroys.repl.run/)).
* `MIDDLE_MAN`(required) - Middle man channel's id.
* `LINK_GEN_BOT`(required) - Username of the bot that generates streamable links for the telegram files ([Bot source](https://github.com/tulir/tgfilestream)).
* `LOG_CHANNEL`(required) - Log channel's id.
* `DATABASE_URL`(required) - Mongodb database URI.
* `AUTH_USERS`(required) - Authorised user(s) id separated by space.
* `MAX_PROCESSES_PER_USER`(optional) - Number of parallel processes each user can have, defaults to 2.
* `MAX_TRIM_DURATION`(optional) - Maximum allowed seconds for trimming. Defaults to 600.

### Run bot
`$ python3 run.py`

Now go to your bot and do a `/start`.

## Contributions
Contributions are welcome.

## Contact
You can contact me [@odysseusmax](https://tx.me/odysseusmax)

## Thanks
Thanks to [Dan](https://github.com/delivrance "Dan") for his [Pyrogram](https://github.com/pyrogram/pyrogram "Pyrogram") library.

Thanks to [Tulir Asokan](https://github.com/tulir "Tulir Asokan") for his [TgFileStream](https://github.com/tulir/tgfilestream "TgFileStream") Bot.
## License
Code released under [The GNU General Public License](LICENSE).
