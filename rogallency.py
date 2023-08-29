import requests
from bs4 import BeautifulSoup
import time
import pdfkit
from urllib import parse
from fake_useragent import UserAgent
import os
import traceback

pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
ua = UserAgent()

BASE_URL = "https://gall.dcinside.com/"

params = {
    'id': 'kpd',
    'search_head' : '20'
}

headers = {
    "Connection" : "keep-alive",
    "Cache-Control" : "max-age=0",
    "sec-ch-ua-mobile" : "?0",
    "DNT" : "1",
    "Upgrade-Insecure-Requests" : "1",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site" : "none",
    "Sec-Fetch-Mode" : "navigate",
    "Sec-Fetch-User" : "?1",
    "Sec-Fetch-Dest" : "document",
    "Accept-Encoding" : "gzip, deflate, br",
    "Accept-Language" : "ko-KR,ko;q=0.9"
    }

i = 14

while True:
    i = i+1
    print(i)
    params['page'] = str(i)
    headers['User-Agent'] = ua.random
    resp = requests.get(BASE_URL+'mgallery/board/lists/', params=params, headers=headers)
    if int(parse.parse_qs(parse.urlparse(resp.url).query)['page'][0]) < i:
        break
    pages = BeautifulSoup(resp.content, 'html.parser')
    contents = pages.find('tbody').find_all('tr')
    for content in contents:
        subject = content.find('td', class_='gall_subject').string
        if subject != '설문':
            link = content.select('a')[0]['href']
            resp = requests.get(BASE_URL+link,headers=headers)
            print(resp)
            page = BeautifulSoup(resp.content, 'html.parser')
            title = page.find('span', class_='title_subject').string
            nickname = page.find('span', class_='nickname').string
            written = page.find('div', class_='write_div')
            for og in written.select('div.og-div'):
                og.decompose()
            if written.find('img') is not None:
                try:
                    headers['Referer'] = BASE_URL+link
                    image_list = written.select('img')
                    for j, image in enumerate(image_list):
                        if image['src'] != '':
                            image_request = requests.get(image['src'], headers=headers)
                            with open('./tmp_img/'+str(j), 'wb') as file:
                                file.write(image_request.content)
                            image['src'] = 'file://'+os.getcwd()+f'/tmp_img/{j}'
                            image['style'] = 'max-width: 100%; height: auto;'
                except:
                    pass
            htmlcode = f'''
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            </head>
            <body>
            <a>
            <h1 align="center">
            {title}
            </h1>
            </a>
            <a>
            <h3 align="right">
            {nickname}
            </h3>
            </a>
            {str(written)}
            </body>
            '''
            filename = title.replace(':',' ').replace('/',' ').replace('.', ' ').strip()
            print(filename+'.pdf')
            while True:
                try:
                    time.sleep(1)
                    options = {'enable-local-file-access': None}
                    pdfkit.from_string(htmlcode, f'./rogallencyclopedia/{filename}.pdf', options=options)
                    for file in os.scandir(os.getcwd()+'/tmp_img'):
                        os.remove(file.path)
                    break
                except Exception as ex:
                    print('error!')
                    print(traceback.format_exc())
                    continue