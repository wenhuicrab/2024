# -*- coding: utf-8 -*-

import os
import sys
import requests
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

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # handle webhook events
    for event in events:
        if isinstance(event, MessageEvent):
            msg = event.message.text
            
            if msg == '統一發票':
                reply_msg = getInvoice()
            elif msg.startswith('/'):
                reply_msg = cambridge(msg[1:])
            elif msg in ['最新消息', '今日新聞']:
                reply_msg = getNews(6)
            else:
                # Default response
                tdnow = datetime.datetime.now()
                reply_msg = tdnow.strftime("%Y/%m/%d, %H:%M:%S") + '\n' + event.message.text
            
            # Reply to the user
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
