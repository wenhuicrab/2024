"""
import requests
from bs4 import BeautifulSoup


#word = input( '請輸入中文字:' )
def read(word):
    url = f'https://dict.revised.moe.edu.tw/search.jsp?md=1&word={word}#searchL'

    html = requests.get( url )
    bs = BeautifulSoup(html.text,'lxml')
    data = bs.find('table', id='searchL')
    try:
        row = data.find_all('tr')[2]
        chinese = row.find('cr').text
        phones = row.find_all('code')
        phone = [e.text for e in phones]
        s = " ".join( phone )
        # s = row.find('sub')
        return( chinese, s )
    except:
        return( '查無此字' )
"""
import requests
from bs4 import BeautifulSoup

def read(word):
    try:
        url = f'https://dict.revised.moe.edu.tw/search.jsp?md=1&word={word}'
        
        html = requests.get(url)
        html.raise_for_status()  # 如果請求失敗，會拋出異常

        bs = BeautifulSoup(html.text, 'lxml')
        data = bs.find('table', id='searchL')
        
        if data:
            row = data.find_all('tr')[1]  # 找到第二個 <tr> 元素，因為第一個通常是表頭
            chinese = row.find('td', class_='main').text.strip()  # 假設中文解釋在 class 為 'main' 的 <td> 元素中
            phones = row.find_all('code')
            phone = [e.text for e in phones]
            phone_str = " ".join(phone)
            return chinese, phone_str
        else:
            return '查無此字'
    
    except requests.exceptions.RequestException as e:
        print('網頁請求失敗:', e)
        return '網頁請求失敗'
    
    except AttributeError as e:
        print('解析 HTML 元素出錯:', e)
        return '解析 HTML 元素出錯'

# 測試程式碼
#word = input('請輸入中文字:')
#result = read(word)
#print(result)
