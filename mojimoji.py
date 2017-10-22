import os.path,sys
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,ImagemapSendMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi('HvlRdc8yEbGXkq/V9cRJ6/+yRgJuZGNFEzx7I7p/TUovvMhuVSwLW54aDFH+M07krwhBs2zDr013S0+kAZyxSMmRYRHn6ja3YzgQniObM3DXo7yv/+vBY5twglEUi43UUg5mIQEBpWZN5hrVkwkX/AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('23172aefb6f71f1e78f643b171b6c389')


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
    print(message_content.content())
    # line_bot_api.reply_message(
    #     event.reply_token,

    # )

if __name__ == "__main__":
    app.run()