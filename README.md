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
* `TRACK_CHANNEL`(optional) - User activity tracking channel's id. Only needed if you want to track and block any user. Disabled by default.

### Run bot
`$ python3 run.py`

Now go to your bot and do a `/start`.

## Supported commands and functions

### Commands

* `/start` - Command to start bot or check whether bot is alive.
* `/settings` - Command to configure bot's behavior'
* `/set_watermark` - Command to add custom watermark text to screenshots. Usage: `/set_watermark watermark_text`

* `/status` - Admin/Auth users only command. Returns number of total users.
* `/ban_user` - Admin/Auth users only command. Command to ban any user. Usage: `/ban_user user_id ban_duration ban_reason`.
* `/unban_user` - Admin/Auth users only command. Command to ban any banned user. Usage: `/unban_user user_id`.

### Functions
* `Screenshot Generation` - Generates screenshots from telegram video files or streaming links. Number of screenshots range from 2-10.
* `Sample Video Generation` - Generates sample video from telegram video files or streaming links. Video duration range from 30s to 150s. Configurable in `/settings`.
* `Video Trimming` - Trims any telegram video files or streaming links. Video duration depends on the environment. By default upto 10 mins (600s).

### Settings
In bot settings.
* `Upload Mode` - Screenshot upload mode. Either `as image file` or `as document file`. Defaults to `as image file`.
* `Watermark` - Watermark text to be embedded to screenshots. Texts upto 30 characters supported. Disabled by default.
* `Watermark Color` - Font color to be used for watermark. Any of `white`, `black`, `red`, `blue`, `green`, `yellow`, `orange`, `purple`, `brown`, `gold`, `silver`, `pink`. Defaults to `white`.
* `Watermark Font Size` - Font size to be used for watermarks. Any of `small(30)`, `medium(40)`, `large(50)`. Defaults to `medium`.
* `Sample Video Duration` - Sample video's duration. Any of `30s`, `60s`, `90s`, `120s`, `150s`. Defaults to `30s`.
* `Screenshot Genetation Mode` - Either `random` or `equally spaced`. Defaults to `equally spaced`.


## Contributions
Contributions are welcome.

## Contact
You can contact me [@odysseusmax](https://tx.me/odysseusmax)

## Thanks
Thanks to [Dan](https://github.com/delivrance "Dan") for his [Pyrogram](https://github.com/pyrogram/pyrogram "Pyrogram") library.

Thanks to [Tulir Asokan](https://github.com/tulir "Tulir Asokan") for his [TgFileStream](https://github.com/tulir/tgfilestream "TgFileStream") Bot.
## License
Code released under [The GNU General Public License](LICENSE).
