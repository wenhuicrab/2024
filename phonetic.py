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