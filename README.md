# [Screenshotit_bot](https://tx.me/screenshotit_bot)
> Telegram Bot For Screenshot Generation.

## Description

An attempt to implement the screenshot generation of telegram files without downloading the entire file. Live version can be found here [@screenshotit_bot](https://tx.me/screenshotit_bot "Screenshot Generator Bot").

## Installation Guide

### Prerequisites
* FFmpeg.
* Python3 (3.6 or higher).

### Local setup
* Clone to local machine.
```
$ git clone https://github.com/odysseusmax/animated-lamp.git
$ cd animated-lamp
````

* Create and activate virtual environment.
```
$ pip3 install virtualenv
$ virtualenv venv
$ source venv/bin/activate
```

* Install dependencies.
```
$ pip3 install -U -r requirements.txt
```

### Environment Variables

Properly setup the environment variables or populate `config.py` with the values (some of the values are sensitive data, so keep them safe).

* `API_ID`(required) - Get your telegram API_ID from [https://my.telegram.org/](https://my.telegram.org/).
* `API_HASH`(required) - Get your telegram API_HASH from [https://my.telegram.org/](https://my.telegram.org/).
* `BOT_TOKEN`(required) - Obtain your bot token from [Bot Father](https://t.me/BotFather "Bot Father").
* `LOG_CHANNEL`(required) - Log channel's id.
* `DATABASE_URL`(required) - Mongodb database URI.
* `AUTH_USERS`(required) - Admin(s) of the bot. User's telegram id separated by space.
* `HOST`(required) - Public URL of file streaming service ([Source](https://github.com/tulir/tgfilestream "TgFileStream")).
* `SESSION_NAME`(optional) - Name you want to call your bot's session, Eg: bot's username.
* `MAX_PROCESSES_PER_USER`(optional) - Number of parallel processes each user can have, defaults to 2.
* `MAX_TRIM_DURATION`(optional) - Maximum allowed trim duration in seconds. Defaults to 600s.
* `TRACK_CHANNEL`(optional) - User activity tracking channel's id. Only needed if you want to track and block any user. Disabled by default.
* `SLOW_SPEED_DELAY`(optional) - Delay required between each request from users in seconds. Defaults to 15s.
* `DEBUG` (optional) - Set some value to use DEBUG logging level. INFO by default.

### Run bot
`$ python3 -m bot`

Now go to your bot and do a `/start`.

## Supported commands and functions

### Commands

**General commands**

* `/start` - Command to start bot or check whether bot is alive.
* `/settings` - Command to configure bot's behavior'
* `/set_watermark` - Command to add custom watermark text to screenshots. Usage: `/set_watermark watermark_text`.

**Admin commands**

> Any user specified in `AUTH_USERS` can use these commands.

* `/status` - Returns number of total users.
* `/ban_user` - Command to ban any user. Usage: `/ban_user user_id ban_duration ban_reason`. `user_id` - telegram id of the user, `ban_duration` - ban duration in days, `ban_reason` - reason for ban. All 3 parameters are required.
* `/unban_user` - Command to unban any banned user. Usage: `/unban_user user_id`. `user_id` - telegram id of the user. The parameter is required.
* `/banned_users` - Command to view all banned users. Usage: `/banned_users`. This takes no parameters.
* `/broadcast` - Command to broadcast some message to all users. Usage: reply `/broadcast` to the message you want to broadcast.

### Functions
* `Screenshot Generation` - Generates screenshots from telegram video files or streaming links. Number of screenshots range from 2-10.
* `Sample Video Generation` - Generates sample video from telegram video files or streaming links. Video duration range from 30s to 150s. Configurable in `/settings`.
* `Video Trimming` - Trims any telegram video files or streaming links.

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
You can contact me [@odysseusmax](https://tx.me/odysseusmax).

## Thanks
Thanks to [Dan](https://github.com/delivrance "Dan") for his [Pyrogram](https://github.com/pyrogram/pyrogram "Pyrogram") library.

Thanks to [Tulir Asokan](https://github.com/tulir "Tulir Asokan") for his [TgFileStream](https://github.com/tulir/tgfilestream "TgFileStream") Bot.

## License
Code released under [The GNU General Public License](LICENSE).
