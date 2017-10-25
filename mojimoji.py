import os,sys,tempfile
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent,PostbackEvent, TextMessage, TextSendMessage,ImageMessage,ImageSendMessage,TemplateSendMessage,ButtonsTemplate,MessageTemplateAction,PostbackTemplateAction
)

app = Flask(__name__)

line_bot_api = LineBotApi('HvlRdc8yEbGXkq/V9cRJ6/+yRgJuZGNFEzx7I7p/TUovvMhuVSwLW54aDFH+M07krwhBs2zDr013S0+kAZyxSMmRYRHn6ja3YzgQniObM3DXo7yv/+vBY5twglEUi43UUg5mIQEBpWZN5hrVkwkX/AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('23172aefb6f71f1e78f643b171b6c389')

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

moji_format = ""

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
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("textmessageハンドラが起動しました")
    line_bot_api.reply_message(
        event.reply_token,
        [TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
        thumbnail_image_url='https://example.com/image.jpg',
        title='もじもじちゃんです',
        text='読み取りたい文字を選んでください！',
        actions=[
            PostbackTemplateAction(
                label='手書き',
                data='our'
            ),
            PostbackTemplateAction(
                label='手書き以外(印刷物など)',
                data='ocr'
            )
        ]
    )
)])

@handler.add(PostbackEvent)
def handle_postback(event):
    post = event.postback
    global moji_format
    moji_format = post.data
    line_bot_api.reply_message(
        event.reply_token,[TextSendMessage(text="画像を送ってくださいね！")])
    return moji_format

@handler.add(MessageEvent,message=ImageMessage)
def handle_img(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    else:
        sorry_text='画像以外は送れません、ごめんなさい!'
        line_bot_api.reply_message(
            event.reply_token, [TextSendMessage(text=sorry_text)])
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
    
    #手書き文字以外の解析
    if moji_format == "ocr":
        params = urllib.parse.urlencode({
            'language': 'unk',
            'detectOrientation ': 'true',
        })

        body = message_content.iter_content()

        try:
            conn = http.client.HTTPSConnection(uri_base)
            conn.request("POST", "/vision/v1.0/ocr?%s" % params, body, headers)
            response = conn.getresponse()
            result = response.read()

            output = ""
            parsed = json.loads(result)
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
                        output += '\n'
                    output += '\n'
        except Exception as e:
            print('Error:')
            print(e)

    #手書き文字の解析
    else:
        print(moji_format)
        body = message_content.iter_content()
        params = urllib.parse.urlencode({'handwriting' : 'true'})
        try:
            conn = http.client.HTTPSConnection(uri_base)
            conn.request('POST','/vision/v1.0/recognizeText%s' % params, body, headers)
            response = conn.getresponse()
            data = response.read()
            output = ""
            parsed = json.loads(data) 
            print("これはパースです")
            print(parsed)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=output))
if __name__ == "__main__":
    app.run()