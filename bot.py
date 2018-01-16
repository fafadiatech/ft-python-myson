"""
bot.py contains bot related classes and functions to send messages and
activate ssh sessions
"""

import paramiko
import textwrap
from telegram import Bot
from functools import wraps
from settings import TELEGRAM_TOKEN
from nltk.chat.eliza import eliza_chatbot
from models import User, Group, ServerInfo
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters

# Initialize bot
my_bot = Bot(token=TELEGRAM_TOKEN)

# store activate ssh session in python dictionary
# try to find better solution for this
ssh_sessions = {}


class SSHclient(object):
    """
    ssh class to connect to given host and execute commands
    """

    def __init__(self, server, username, password):
        """
        initialize ssh paramiko client and connect to given host
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(server, username=username, password=password)
        self.user_id = ""

    def check_connection(self):
        """
        check connection is active before executing any command
        """
        transport = self.ssh.get_transport()
        if transport and transport.is_active():
            return True
        return False

    def remove_session(self, user_id):
        """
        remove session for given user id
        """
        if user_id in ssh_sessions:
            del ssh_sessions[user_id]

    def exec_cmd(self, cmd):
        """
        try to execute command on host and return the result,
        before executing command check connection is active
        """
        try:
            if self.check_connection():
                stdin, stdout, stderr = self.ssh.exec_command(cmd)
                if stdout.channel.recv_exit_status() == 0:
                    result = stdout.read()
                    return result.decode("utf-8")
                else:
                    result = stderr.read()
                    return result.decode("utf-8")
            else:
                self.remove_session(self.user_id)
                return "Your ssh session is expired, start new ssh session to continue"
        except Exception as e:
            return e

    def close_conn(self):
        """
        close ssh session
        """
        self.ssh.close()


def restricted(func):
    """
    This decorator restricts access of a command to users
    """
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        user_obj = User()
        user = user_obj.get(uid=user_id, is_admin=True)
        if not user:
            msg = "Unauthorized access denied for {}.".format(user_id)
            update.message.reply_text(msg)
            update.message.reply_text('Go away.')
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def hello(bot, update):
    """
    Greet the user with their first name and Telegram ID.
    """
    user_firstname = update.message.from_user.first_name
    user_id = update.message.from_user.id
    return update.message.reply_text('Hello {}, your Telegram ID is {}'.format(user_firstname, user_id))


def random_reply(bot, update):
    """
    send any random replies from eliza
    """
    text = update.message.text
    reply = eliza_chatbot.respond(text)
    bot.sendMessage(chat_id=update.message.chat_id, text=reply)


def send_msg(bot, from_id, chat_id, text, parse_mode=None):
    """
    send msg to specific user
    """
    try:
        if parse_mode:
            bot.sendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode)
        else:
            bot.sendMessage(chat_id=chat_id, text=text)
    except Exception as e:
        bot.sendMessage(chat_id=from_id, text=e.message)


def send_photo(bot, from_id, chat_id, photo):
    """
    send photo to specific user
    """
    try:
        bot.sendPhoto(chat_id=chat_id, photo=photo)
    except Exception as e:
        bot.sendMessage(chat_id=from_id, text=str(e))


def send_document(bot, from_id, chat_id, document, filename):
    """
    send document to specific user
    """
    try:
        bot.sendDocument(chat_id=chat_id, document=document, filename=filename)
    except Exception as e:
        bot.sendMessage(chat_id=from_id, text=str(e))


@restricted
def start_ssh_session(bot, update, args):
    """
    start ssh session to given server for authorized user,
    validate user id in serverinfo model
    """
    if args:
        user_id = update.message.from_user.id
        server_name = args[0]
        serverinfo_obj = ServerInfo()
        server = serverinfo_obj.get(server_name=server_name)
        if not server:
            text = "Incorrect server name: {0}, Please provider correct server name".format(
                server_name)
            bot.sendMessage(chat_id=user_id, text=text)
        if user_id not in server['users']:
            text = "Access denied for {0}. You can not access {1}".format(
                user_id, server_name)
            bot.sendMessage(chat_id=user_id, text=text)
        server_ip = server['server_ip']
        username = server['server_username']
        password = server['server_password']
        ssh = SSHclient(server_ip, username, password)
        ssh_sessions[user_id] = ssh
        ssh.user_id = user_id
        text = "session started execute command using /cmd"
        bot.sendMessage(chat_id=user_id, text=text)
    else:
        user_id = update.message.from_user.id
        text = "please provide server name"
        bot.sendMessage(chat_id=user_id, text=text)


@restricted
def execute_command_server(bot, update, args):
    """
    execute command on server and send reply to telegram user
    """
    user_id = update.message.from_user.id
    ssh = ssh_sessions.get(user_id)
    if not ssh:
        text = "you dont have any ssh session running"
        bot.sendMessage(chat_id=user_id, text=text)
    if not args:
        text = "please provide command to execute"
        bot.sendMessage(chat_id=user_id, text=text)
    cmd = " ".join(args)
    result = ssh.exec_cmd(cmd)
    if len(result) > 4096:
        results = textwrap.wrap(result, 4096)
        for result in results:
            bot.sendMessage(chat_id=user_id, text=result)
    else:
        bot.sendMessage(chat_id=user_id, text=result)


@restricted
def close_ssh_connection(bot, update, args):
    """
    close currently running ssh connection of user
    """
    user_id = update.message.from_user.id
    ssh = ssh_sessions.get(user_id)
    if not ssh:
        text = "you dont have any ssh session running"
        bot.sendMessage(chat_id=user_id, text=text)
    ssh.close_conn()
    ssh.remove_session(user_id)
    text = "ssh session closed successfully"
    bot.sendMessage(chat_id=user_id, text=text)


if __name__ == '__main__':
    """
    telegram updater handler and commands registeration
    """
    updater = Updater(TELEGRAM_TOKEN)
    reply_handler = MessageHandler([Filters.text], random_reply)
    updater.dispatcher.add_handler(CommandHandler('hello', hello))
    updater.dispatcher.add_handler(CommandHandler('hi', hello))
    updater.dispatcher.add_handler(CommandHandler(
        'register', register, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler(
        'ssh', start_ssh_session, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler(
        'cmd', execute_command_server, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler(
        'exit', close_ssh_connection, pass_args=True))
    updater.dispatcher.add_handler(reply_handler)
    updater.start_polling()
    updater.idle()
