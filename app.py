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
import random
import datetime
from bs4 import BeautifulSoup
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

# Global variables to track multiplication test state
multiplication_ing = False
num1 = None
num2 = None
correct_answer = None

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

def index(request):
    return HttpResponse("hello")

def getInvoice():
    url = "https://invoice.etax.nat.gov.tw"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers = {'User-Agent': user_agent}
    html = requests.get(url, headers=headers)
    html.encoding = 'utf-8'
    soup = BeautifulSoup(html.text, 'html.parser')

    period = soup.find("a", class_="etw-on")
    rr = period.text + "\n"

    nums = soup.find_all("p", class_="etw-tbiggest")
    rr += "特別獎：" + nums[0].text + "\n"
    rr += "特獎：" + nums[1].text + "\n"
    rr += "頭獎：" + nums[2].text.strip() + " " + nums[3].text.strip() + " " + nums[4].text.strip()

    return rr

def cambridge(word):
    url = 'https://dictionary.cambridge.org/dictionary/english-chinese-traditional/' + word
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers = {'User-Agent': user_agent}
    web_request = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_request.text, "html.parser")
    entries = soup.find_all("div", class_="entry-body__el")
    rr = ""
    for entry in entries:
        rr += entry.find('div', class_="posgram").text + '\n'
        i = 1
        ddefs = entry.find_all("div", class_="def-body")
        for ddef in ddefs:
            tran = ddef.find('span')
            rr += str(i) + '.' + tran.text + "\n"
            i += 1
    rr += "\n出處:" + url
    return rr

def getNews(num=10):
    """"擷取中央社新聞"""
    url = "https://www.cna.com.tw/list/aall.aspx"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    html = requests.get(url, headers=headers)

    soup = BeautifulSoup(html.text, 'html.parser')
    soup.encoding = 'utf-8'

    allnews = soup.find(id="jsMainList")
    nn = allnews.find_all('li')

    mm = ""
    for n in nn[:num]:
        mm += n.find('div', class_='date').text + ' '
        mm += n.find('h2').text + '\n'
        mm += 'https://www.cna.com.tw/' + n.find('a').get('href') + '\n'
        mm += '-' * 30 + '\n'
    return mm

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        msg = event.message.text

        if msg.startswith('*'):
            word_to_lookup = msg[1:].strip()
            reply_msg = cambridge(word_to_lookup)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
            )
        elif msg in ['最新消息', '今日新聞']:
            reply_msg = getNews(6)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
            )
        elif msg == '統一發票':
            reply_msg = getInvoice()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
            )
        elif msg == '九九乘法':
            global multiplication_ing, num1, num2, correct_answer
            if multiplication_ing:
                multiplication_ing = False
                reply_msg = "測驗結束"
            else:
                multiplication_ing = True
                num1 = random.randint(1, 9)
                num2 = random.randint(1, 9)
                correct_answer = num1 * num2
                reply_msg = f"測驗開始\n{num1} * {num2} 是多少?"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
            )
        elif msg == '結束測驗':
            if multiplication_ing:
                multiplication_ing = False
                reply_msg = "測驗已結束"
            else:
                reply_msg = "目前沒有進行中的測驗"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
            )
        elif multiplication_ing and msg.isdigit():
            try:
                user_answer = int(msg)
                if user_answer == correct_answer:
                    reply_msg = "恭喜你答對了!\n"
                    num1 = random.randint(1, 9)
                    num2 = random.randint(1, 9)
                    correct_answer = num1 * num2
                    reply_msg += f"下一題: {num1} * {num2} 是多少?"
                else:
                    reply_msg = "嗯...再多想想答案吧\n"
            except ValueError:
                reply_msg = "請輸入有效的數字!\n"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
            )
        else:
            tdnow = datetime.datetime.now()
            reply_msg = tdnow.strftime("%Y/%m/%d, %H:%M:%S") + '\n' + event.message.text
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
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
