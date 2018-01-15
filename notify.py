# flask api to send notifications and send group messages
from io import BytesIO
from models import User, Group
from flask import Flask, request, jsonify
from groups import create_group, add_member_to_group
from bot import send_msg, my_bot, send_photo, send_document


# flask app
app = Flask(__name__)


class Error(Exception):
    """
    error class to handle api exception
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['ok'] = 0
        return rv


# register flask api error class
@app.errorhandler(Error)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/api/notify/')
def send_notification():
    """
    send notification to given telegram user
    """
    username = request.args.get("username", "")
    to_id = request.args.get("to", "")
    text = request.args.get("msg", "")
    msg_type = request.args.get("type", None)  # "HTML" or "Markdown"

    if not username:
        msg = "required parameter username missing"
        raise Error(msg)

    if not to_id:
        msg = "required parameter to missing"
        raise Error(msg)

    if not text:
        msg = "message can not be blank"
        raise Error(msg)

    user_obj = User()
    user = user_obj.get(username=username)

    if not user:
        msg = "you dont have permisson to send notification"
        raise Error(msg)

    to = user_obj.get(username=to_id)
    if not to:
        group_obj = Group()
        to = group_obj.get(group_name=to_id)
        if not to:
            msg = "invalid to id"
            raise Error(msg)
        else:
            send_msg(my_bot, user["uid"], -to["gid"], text, msg_type)
            return jsonify({"ok": 1})
    send_msg(my_bot, user["uid"], to["uid"], text, msg_type)
    return jsonify({"ok": 1})


@app.route('/api/photo/', methods=['POST'])
def send_image():
    """
    send image/photo to given telegram user
    """
    username = request.args.get("username", "")
    to_id = request.args.get("to", "")
    photo_file = request.files.get("photo", "")
    photo = request.form.get("photo", "")

    if not username:
        msg = "username missing"
        raise Error(msg)

    if not to_id:
        msg = "to id missing"
        raise Error(msg)

    if not any([photo_file, photo]):
        msg = "photo can not be blank"
        raise Error(msg)

    user_obj = User()
    user = user_obj.get(username=username)

    if not user:
        msg = "you dont have permisson to send notification"
        raise Error(msg)

    to = user_obj.get(username=to_id)
    if not to:
        group_obj = Group()
        to = group_obj.get(group_name=to_id)
        if not to:
            msg = "invalid to id"
            raise Error(msg)
        else:
            if photo:
                send_photo(my_bot, user["uid"], to["gid"], photo)
            else:
                out = BytesIO()
                out.write(photo_file.stream.read())
                out.seek(0)
                send_photo(my_bot, user["uid"], to["gid"], out)
            return jsonify({"ok": 1})
    if photo:
        send_photo(my_bot, user["uid"], to["uid"], photo)
    else:
        out = BytesIO()
        out.write(photo_file.stream.read())
        out.seek(0)
        send_photo(my_bot, user["uid"], to["uid"], out)
    return jsonify({"ok": 1})


@app.route('/api/document/', methods=['POST'])
def upload_document():
    """
    send document to given telegram user
    """
    username = request.args.get("username", "")
    to_id = request.args.get("to", "")
    document_file = request.files.get("document", "")

    if not username:
        msg = "username missing"
        raise Error(msg)

    if not to_id:
        msg = "to id missing"
        raise Error(msg)

    if not document_file:
        msg = "document can not be blank"
        raise Error(msg)

    user_obj = User()
    user = user_obj.get(username=username)

    if not user:
        msg = "you dont have permisson to send notification"
        raise Error(msg)

    to = user_obj.get(username=to_id)
    if not to:
        group_obj = Group()
        to = group_obj.get(group_name=to_id)
        if not to:
            msg = "invalid to id"
            raise Error(msg)
        else:
            out = BytesIO()
            out.write(document_file.stream.read())
            out.seek(0)
            send_document(my_bot, user["uid"], to[
                          "gid"], out, str(document_file.filename))
            return jsonify({"ok": 1})
    out = BytesIO()
    out.write(document_file.stream.read())
    out.seek(0)
    send_document(my_bot, user["uid"], to["uid"],
                  out, str(document_file.filename))
    return jsonify({"ok": 1})


@app.route('/api/create/group/')
def create_group_api():
    """
    create telegram group api
    """
    group_name = request.args.get("group", "")
    uids = request.args.getlist("uids", type=int)
    result, error = create_group(uids, group_name)
    if not error:
        result = result.to_dict()
        group_id = result['chats'][0]['id']
        group = Group()
        group.create(gid=group_id, group_name=group_name, members=uids)
        return jsonify({"ok": 1})
    return jsonify({"ok": 0})


if __name__ == '__main__':
    app.run()
