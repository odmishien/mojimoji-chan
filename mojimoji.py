import os, sys, tempfile, http.client, urllib.request, urllib.parse, urllib.error, base64, json
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,ImageSendMessage,TemplateSendMessage
)

app = Flask(__name__)
LINE_API_KEY = os.environ(["LINE_API_KEY"])
WEBHOOK_HANDLER_KEY = os.environ(["WEBHOOK_HANDLER_KEY"])
AZURE_SUBSC_KEY = os.environ(["AZURE_SUBSC_KEY"])

line_bot_api = LineBotApi(LINE_API_KEY)
handler = WebhookHandler(WEBHOOK_HANDLER_KEY)

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

    uri_base = 'eastasia.api.cognitive.microsoft.com'
    headers = {
        # Request headers.
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': AZURE_SUBSC_KEY,
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
        print(parsed['regions'])
        if parsed ['regions'] == []:
            output = "文字は見当たりません。。。"
        else:
            for txt_lines in parsed['regions']:
                for txt_words in txt_lines['lines']:
                    for txt_word in txt_words['words']:
                        if parsed['language'] == 'ja':
                            output += txt_word['text']
                        else:
                            output += txt_word['text'] + ' '
                    output += "\n"
    except Exception as e:
        print('Error:')
        print(e)
        output = "画像の読み込みに失敗しました…ワタシが悪いんです…"

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=output))
if __name__ == "__main__":
    app.run()
