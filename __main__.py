import os
import ssl
import sys
import time
from datetime import datetime
from itertools import count
from urllib.request import Request, urlopen

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

from collection import crawler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def crawling_pelicana():
    results = []

    for page in count(start=113):
        url = 'https://pelicana.co.kr/store/stroe_search.html?branch_name=&gu=&si=&page=%d' % page
        html = crawler.crawling(url)

        bs = BeautifulSoup(html, 'html.parser')
        tag_table = bs.find('table', attrs={'class': 'table mt20'})
        tag_tbody = tag_table.find('tbody')
        tags_tr = tag_tbody.findAll('tr')

        #끝 검출
        if len(tags_tr) == 0:
            break

        for tag_tr in tags_tr:
            strings = list(tag_tr.strings)
            name = strings[1]
            address = strings[3]
            sidogu = address.split()[:2]
            results.append((name, address) + tuple(sidogu))

    # store
    table = pd.DataFrame(results, columns=['name', 'address', 'sido', 'gugun'])
    table.to_csv('__results__/pelicana.csv', encoding='utf-8', mode='w', index=True)

    for t in results:
        print(t)


def crawling_nene():
    results = []
    prev_first = ''

    for page in count(45):
        url = 'https://nenechicken.com/17_new/sub_shop01.asp?ex_select=1&ex_select2=&IndexSword=&GUBUN=A&page=%d' % page
        try:
            request = Request(url)
            response = urlopen(request)
            receive = response.read()
            html = receive.decode('utf-8', errors='replace')

            print(f'{datetime.now()}: success for request [{url}]')
        except Exception as e:
            print(f'{e} : {datetime.now()}', file=sys.stderr)
            continue

        bs = BeautifulSoup(html, 'html.parser')
        names = bs.findAll('div', attrs={'class': 'shopName'})

        if names[0].string == prev_first:
            break
        else:
            prev_first = names[0].string

        addresses = bs.findAll('div', attrs={'class': 'shopAdd'})

        for num in range(0, len(names)):
            name = names[num].string
            address = addresses[num].string
            sidogu = address.split()[:2]
            results.append((name, address) + tuple(sidogu))

    # store
    table = pd.DataFrame(results, columns=['name', 'address', 'sido', 'gugun'])
    table.to_csv('/root/crawling-results/nene.csv', encoding='utf-8', mode='w', index=True)

    for t in results:
        print(t)


def crawling_kyochon():
    results = []
    for sido1 in range(1, 2):
        for sido2 in range(1):
            url = 'http://www.kyochon.com/shop/domestic.asp?sido1=%d&sido2=%d' % (sido1, sido2)
            html = crawler.crawling(url)

            #끝검출
            if html is None:
                break

            bs = BeautifulSoup(html, 'html.parser')
            tag_ul = bs.find('ul', attrs={'class': 'list'})
            tags_span = tag_ul.findAll('span', attrs={'class': 'store_item'})

            for tag_span in tags_span:
                strings = list(tag_span.strings)
                # print(strings)

                name = strings[1]
                address = strings[3].strip('\r\n\t')
                sidogu = address.split()[:2]
                results.append((name, address) + tuple(sidogu))

    for t in results:
        print(t)

    # store
    table = pd.DataFrame(results, columns=['name', 'address', 'sido', 'gugun'])
    table.to_csv('__results__/kyochon.csv', encoding='utf-8', mode='w', index=True)


def crawling_goobne():
    url = 'http://www.goobne.co.kr/store/search_store.jsp'

    # 첫 페이지 로딩
    wd = webdriver.Chrome('C:\cafe24\chromedriver_win32\chromedriver.exe')
    wd.get(url)
    time.sleep(2)

    results = []
    for page in count(1):
        #자바스크립트 실행
        script = 'store.getList(%d)' % page
        wd.execute_script(script)
        print(f'{datetime.now()}: success for request [{script}]')
        time.sleep(2)

        # 실행결과HTML(동적으로 렌더링 된 HTML) 가져오기
        html = wd.page_source

        # parsing with bs4
        bs = BeautifulSoup(html, 'html.parser')
        tag_tbody = bs.find('tbody', attrs={'id': 'store_list'})
        tags_tr = tag_tbody.findAll('tr')

        # detect last page
        if tags_tr[0].get('class') is None:
            break

        for tag_tr in tags_tr:
            strings = list(tag_tr.strings)
            name = strings[1]
            address = strings[6]
            sidogu = address.split()[:2]

            results.append((name, address) + tuple(sidogu))

    wd.quit()
    # for result in results:
    #     print(result)


if __name__ == '__main__':
    # pelicana
    # crawling_pelicana()

    # nene 과제
    crawling_nene()

    # kyochon
    # crawling_kyochon()

    # goobne
    # crawling_goobne()