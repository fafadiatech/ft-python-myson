# Myson :- Telegram bot

[![N|Solid](http://www.fafadiatech.com/static/img/ftlogo.png)](http://www.fafadiatech.com/)

Myson is Telegram bot, to help fafadia-tech Team notify as well as execute various activities.


# Features

  - Notify - Send notification on a myson bot
  - Photo - Send a linked photo to user or group
  - Document - Send a document to user or group
  - Groups -  Create telegram groups or add member to existing group
  - Linux Shell - Access linux server from telegram personal chat window (Interactive commands are not implemented for example 'top' command)

### Libraries used

Myson uses following libraries

* [Telegram python bot](https://github.com/python-telegram-bot/python-telegram-bot) - Python interface for the Telegram Bot API
* [Telethon](https://github.com/LonamiWebs/Telethon) - Telethon is Telegram client implementation in Python 3
* [Flask](http://flask.pocoo.org/) - Flask is a microframework for Python
* [Paramiko](http://www.paramiko.org/) - Paramiko is a Python implementation of the SSHv2 protocol


### Installation
clone the repository
```sh
$ git clone git@bitbucket.org:fafadiatech/myson.git
```
create virtualenv
```sh
$ mkvirtualenv myson
$ workon myson
```

Install the dependencies and devDependencies and start the server.

* create telegram bot (https://core.telegram.org/bots check point number 6)
* create telegram app id (https://core.telegram.org/api/obtaining_api_id)
* add settings in settings.py
```sh
$ cd myson
$ pip install -r requirements.txt
$ python notify.py
$ python bot.py
```

### Development
Verify the deployment by navigating to your server address in your preferred browser.

```sh
127.0.0.1:5000
```


### Todos
 - Create frontend
 - Implement ssh session storage
 






