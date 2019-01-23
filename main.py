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
import json
import requests
from datetime import date
from pprint import *
import pymysql.cursors

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
    # userId を取得 (1)
    body_json = json.loads(body)
    app.logger.info('User Id: {}'.format(body_json['events'][0]['source']['userId']))
    # handle webhook body
    userAdd(body_json)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def userAdd(body):
    event = body['events'][0]
    # print(event['type'])
    if event['type']=='follow':
        user_id = event['source']['userId']
        profile=line_bot_api.get_profile(user_id)
        user_name = profile.display_name
        print(user_id)
        print(user_name)
        register(user_id,user_name)
    elif event['type']=='unfollow':
        user_id = event['source']['userId']
        print(user_id)
        unregister(user_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
    users = selectUsers()
    today = parseClass()
    line_bot_api.multicast(users,TextSendMessage(text=today))

def parseClass():
    d = date.today()
    day = d.weekday()
    # print(day)
    try:
        with open('class.json','r') as f:
            class_data = json.load(f)
            # pprint(class_data[day])
    finally:
        today = []
        for row in class_data[day].items():
            if row[1] != '':
                today.append(row[0]+':'+row[1])
        # pprint(today)
        today = map(str,today)
        today = '\n'.join(today)
    return today
def selectUsers():
    connect = pymysql.connect(user=settings.user,passwd=settings.password,host=settings.host,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor,db=settings.db)
    try:
        with connect.cursor() as cursor:
            sql = 'SELECT `userID` FROM `users` WHERE 1'
            cursor.execute(sql)
            results = cursor.fetchall()
            users = []
            for i in results:
                users.append(i['userID'])
    finally:
        connect.close()
    # print(users)
    return users
def register(id,name):
    connect = pymysql.connect(user=settings.user,passwd=settings.password,host=settings.host,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor,db=settings.db)
    try:
        with connect.cursor() as cursor:
            sql = 'INSERT INTO users (userID,Name) VALUES (%s,%s)'
            cursor.execute(sql,(id,name))
            connect.commit()
            # print(result)
    finally:
        connect.close()
def unregister(id):
    connect = pymysql.connect(user=settings.user,passwd=settings.password,host=settings.host,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor,db=settings.db)
    try:
        with connect.cursor() as cursor:
            sql = 'DELETE FROM users WHERE userID=%s'
            cursor.execute(sql,id)
            connect.commit()
            # print(result)
    finally:
        connect.close()

def pushClass():
    users = selectUsers()
    today = parseClass()
    line_bot_api.multicast(users,TextSendMessage(text=today))

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
    pushClass()
