"""
grops module is used for 

1. create telegram groups 
2. add group members
"""

from telethon import TelegramClient
from telethon.tl.types import InputUser
from settings import API_ID, API_HASH, PHONE, SESSION_NAME
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.functions.messages import AddChatUserRequest


# initialize telegram api access variables
api_id = API_ID
api_hash = API_HASH
phone = PHONE
client = TelegramClient(SESSION_NAME, api_id, api_hash)
client.connect()


def get_input_user(uid):
    """
    create telegram user instance
    """
    return InputUser(uid, 0)


def create_group(uids, group_name):
    """
    create telegram group for given users list
    """
    users = list(map(get_input_user, uids))
    group = CreateChatRequest(users, group_name)
    try:
        result = client.invoke(group)
        return result, False
    except Exception as e:
        return e, True


def add_member_to_group(uid, group_id, fwd_limit=10):
    """
    add member to existing group
    """
    user = get_input_user(uid)
    user_request = AddChatUserRequest(group_id, user, fwd_limit)
    try:
        result = client.invoke(user_request)
        return result, False
    except Exception as e:
        return e, True
