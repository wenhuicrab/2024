# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


import os
import sys
import phonetic as ph
import aaaaa as a99 
import random
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def multiplication_quiz():
    correct_count = 0  # 初始化正確答題計數器
    
    while correct_count < 10:  # 當正確答題計數器小於 10 時持續出題
        # 隨機選擇兩個數字作為題目
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        
        # 計算正確答案
        correct_answer = num1 * num2
        
        while True:  # 使用內部迴圈處理輸入錯誤的情況
            try:
                # 提示題目並讀取使用者的回答
                user_answer = int(input(f"{num1} * {num2}是多少? "))
                
                # 檢查答案是否正確
                if user_answer == correct_answer:
                    print("恭喜你答對了!")
                    correct_count += 1  # 正確答題計數器加一
                    print(f"已經答對了 {correct_count} 題！\n")
                    break  # 跳出內部迴圈，出下一題
                else:
                    print("嗯...再多想想答案吧\n")
                    
            except ValueError:
                print("請輸入有效的數字!")
    
    # 當答對十題時，顯示鼓勵訊息
    print("恭喜你成功答對十題，做得很好！")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ph.read(event.message.text));
        )
          # Call your multiplication quiz function here
        elif event.message.text == '九九乘法表':  # 假設觸發條件是收到文字訊息 '九九乘法表'
            multiplication_quiz(event.reply_token)
             else:
                 line_bot_api.reply_message(
                     event.reply_token,
                    TextSendMessage(text="請輸入 '九九乘法表' 來觸發九九乘法表")
            )
        
      


    return 'OK'
if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
