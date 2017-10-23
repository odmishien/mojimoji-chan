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
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    else:
        sorry_text='画像以外は送れません、ごめんなさい!'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=sorry_text))
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    
    import http.client, urllib.request, urllib.parse, urllib.error, base64, json
    subscription_key = 'f4f305f4d10548e6abe86b32e98852b0'
    uri_base = 'westcentralus.api.cognitive.microsoft.com'

    headers = {
        # Request headers.
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key,
    }

    params = urllib.parse.urlencode({
        'language': 'unk',
        'detectOrientation ': 'true',
    })

    body = message_content.iter_content()

    try:
        conn = http.client.HTTPSConnection(uri_base)
        conn.request("POST", "/vision/v1.0/ocr?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()

        output = ""
        parsed = json.loads(data)
        print(parsed)
        for txt_lines in parsed['regions']:
            for txt_words in txt_lines['lines']:            
                for txt_word in txt_words['words']:
                    if parsed['language'] == 'ja':
                        output += txt_word['text']
                    else:
                        output += txt_word['text'] + ' '
                output += '\n'
            output += '\n'
    except Exception as e:
        print('Error:')
        print(e)

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=output))
if __name__ == "__main__":
    app.run()