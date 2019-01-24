from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ButtonsTemplate,MessageAction
)
import settings
import os
import generateReply

app = Flask(__name__)

line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.access_secret)

@app.route("/")
def hello_world():
    return "hello world"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    word = generateReply.makeReply(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=word))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
