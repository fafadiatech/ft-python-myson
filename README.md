# Myson: Pythonic Bot to send notifications to Telegram

Myson is Telegram bot, to helps teams to get notifications and execute various shell commands. Following are few usecases for which Myson was built:

1. Get notification of different events from a remote server
1. Allow execution of various shell commands from Telegram application

# Features

1. Notify: Send notification on a myson bot
1. Photo: Send a linked photo to user or group
1. Document: Send a document to user or group
1. Group Management: Create telegram groups or add member to existing group
1. Linux Shell: Access linux server from telegram personal chat window (Interactive commands are not implemented for example `top` command)

# Dependencies

Myson uses following libraries 

* [Telegram python bot](https://github.com/python-telegram-bot/python-telegram-bot) - Pythonic interface to Telegram Bot API
* [Telethon](https://github.com/LonamiWebs/Telethon) - Telethon is Telegram client implementation in Python 3
* [Flask](http://flask.pocoo.org/) - Flask is a microframework for Python
* [Paramiko](http://www.paramiko.org/) - Paramiko is a Python implementation of the SSHv2 protocol


# Installation

1. Clone the repository 
  ```ssh
  git clone git@bitbucket.org:fafadiatech/myson.git
  ```
2. Create virtualenv
  ```ssh
  mkvirtualenv myson
  workon myson
  ```
3. Install required dependencies and start the server
  - Create [telegram bot](https://core.telegram.org/bots), You want to check #6 
  - Create [telegram app id](https://core.telegram.org/api/obtaining_api_id)
  - Update `settings.py`
    ```sh
    cd myson
    pip install -r requirements.txt
    python notify.py
    python bot.py
    ```

# Development

Verify the deployment by navigating to your server address in your preferred browser.

```sh
127.0.0.1:5000
```

### TODOs

- Create frontend
- Implement ssh session storage
 






