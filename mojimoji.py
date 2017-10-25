import os,sys,tempfile
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
        print(parsed['regions'])
        if parsed ['regions'] == []:
            output = "文字は見当たりません。。。"
        else:
            for txt_lines in parsed['regions']:
                for txt_words in txt_lines['lines']:            
                    for txt_word in txt_words['words']:
                        if parsed['language'] == 'ja':
                            output += txt_word['text'] + "\n"
                        else:
                            output += txt_word['text'] + ' '
    except Exception as e:
        print('Error:')
        print(e)

    #翻訳機能
    from microsofttranslator import Translator
    if parsed['language'] != "ja":
        accessToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZSI6Imh0dHBzOi8vZGV2Lm1pY3Jvc29mdHRyYW5zbGF0b3IuY29tLyIsInN1YnNjcmlwdGlvbi1pZCI6IjhkNGFmOTU5Y2EzYzQ4YjhhMTIxZmMyODEyM2M2YjY0IiwicHJvZHVjdC1pZCI6IlNwZWVjaFRyYW5zbGF0b3IuUzMiLCJjb2duaXRpdmUtc2VydmljZXMtZW5kcG9pbnQiOiJodHRwczovL2FwaS5jb2duaXRpdmUubWljcm9zb2Z0LmNvbS9pbnRlcm5hbC92MS4wLyIsImF6dXJlLXJlc291cmNlLWlkIjoiL3N1YnNjcmlwdGlvbnMvZmQxYTRjNDEtNjdjYy00ZDUzLThkZGItNTEyZWUxOThjNGQwL3Jlc291cmNlR3JvdXBzL3dheS9wcm92aWRlcnMvTWljcm9zb2Z0LkNvZ25pdGl2ZVNlcnZpY2VzL2FjY291bnRzL21vamltb2ppIiwiaXNzIjoidXJuOm1zLmNvZ25pdGl2ZXNlcnZpY2VzIiwiYXVkIjoidXJuOm1zLm1pY3Jvc29mdHRyYW5zbGF0b3IiLCJleHAiOjE1MDg5MTcxNDR9.j2rESxaxufqLmhWwjXAmNUHSpjGKUIvHeeMsBTrgzok'
        translator = Translator(accessToken)
        ja = translator.translate(text=output,to_lang='ja',from_lang=parsed['language'])
        print(ja)

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=output))
if __name__ == "__main__":
    app.run()