# [ScreenShot Bot](https://tx.me/ScreenShotTGBot)
> Telegram Bot For Screenshot Generation.

## Description

An attempt to implement the screenshot generation of telegram files without downloading the entire file. Live version can be found here [@ScreenShot Bot](https://tx.me/ScreenShotTGBot).
> Screenshot Generation with Custom Watermark---Sample Video Generation---Trim video.

## Installation Guide

### You can also tap the Deploy To Heroku button below to deploy straight to Heroku!

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/TGExplore/Screenshot-Bot)

### Watch our YouTube video for more details - [Telegram Screenshot | Trim | Sample Video Generator Bot](https://youtu.be/Fsc-ZUvdO20)

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
* `SESSION_NAME`(required) - Name you want to call your bot's session, Eg: bot username.
* `LOG_CHANNEL`(required) - Log channel's id.
* `DATABASE_URL`(required) - Mongodb database URI.
* `AUTH_USERS`(required) - Authorised user(s) id separated by space.
* `HOST`(required) - Public URL of streaming service ([Source](https://github.com/TGExplore/musical-waddle)).
* `MAX_PROCESSES_PER_USER`(optional) - Number of parallel processes each user can have, defaults to 2.
* `MAX_TRIM_DURATION`(optional) - Maximum allowed seconds for trimming. Defaults to 600.
* `TRACK_CHANNEL`(optional) - User activity tracking channel's id. Only needed if you want to track and block any user. Disabled by default.
* `SLOW_SPEED_DELAY`(optional) - Delay required between each request. Defaults to 15s.

### Run bot
`$ python3 -m bot`

Now go to your bot and do a `/start`.

## Supported commands and functions

### Commands

* `/start` - Command to start bot or check whether bot is alive.
* `/settings` - Command to configure bot's behavior'
* `/set_watermark` - Command to add custom watermark text to screenshots. Usage: `/set_watermark watermark_text`.

* `/status` - Admin/Auth users only command. Returns number of total users.
* `/ban_user` - Admin/Auth users only command. Command to ban any user. Usage: `/ban_user user_id ban_duration ban_reason`. `user_id` - telegram id of the user, `ban_duration` - ban duration in days, `ban_reason` - reason for ban. All 3 parameters are required.
* `/unban_user` - Admin/Auth users only command. Command to ban any banned user. Usage: `/unban_user user_id`. `user_id` - telegram id of the user. The parameter is required.
* `/banned_users` - Admin/Auth users only command. Command to view all banned users. Usage: `/banned_users`. This takes no parameters.
* `/broadcast` - Admin/Auth user only command. Command to broadcast some message to all users. Usage: reply `/broadcast` to the message you want to broadcast.

### Functions
* `Screenshot Generation` - Generates screenshots from telegram video files or streaming links. Number of screenshots range from 2-10.
* `Manual Screenshot` - Generates screenshots of specific time. Number of screenshots range from 1-10.
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
You can contact me [@InFoTelGroup](https://tx.me/InFoTelGroup).

## Thanks

Thanks to [@odysseusmax](https://tx.me/odysseusmax) for his [animated-lamp](https://github.com/odysseusmax/animated-lamp) Bot.

Thanks to [Dan](https://github.com/delivrance "Dan") for his [Pyrogram](https://github.com/pyrogram/pyrogram "Pyrogram") library.

Thanks to [Tulir Asokan](https://github.com/tulir "Tulir Asokan") for his [TgFileStream](https://github.com/tulir/tgfilestream "TgFileStream") Bot.

## License
Code released under [The GNU General Public License](LICENSE).
