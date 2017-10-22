import os,sys,tempfile
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,ImageSendMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi('HvlRdc8yEbGXkq/V9cRJ6/+yRgJuZGNFEzx7I7p/TUovvMhuVSwLW54aDFH+M07krwhBs2zDr013S0+kAZyxSMmRYRHn6ja3YzgQniObM3DXo7yv/+vBY5twglEUi43UUg5mIQEBpWZN5hrVkwkX/AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('23172aefb6f71f1e78f643b171b6c389')

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return ''


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="画像を送ってクレメンス"))

@handler.add(MessageEvent,message=ImageMessage)
def handle_img(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='jpg-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     ImageSendMessage(
    #         original_content_url='test.jpg',
    #         preview_image_url='test.jpg'
    #     )
    # )

    
    # line_bot_api.reply_message(
    #     event.reply_token,

    # )

if __name__ == "__main__":
    app.run()