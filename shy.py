''' 
Title   : 请不要害羞豆瓣小组图片爬虫
Author  : huggo 
DateTime: 2018-08-27
'''

import requests
from urllib import parse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import time
from multiprocessing import Pool

# 代理
proxy = ''
proxies = {
    'https' : 'https://'+proxy,
}

baseUrl = 'https://www.douban.com/group/haixiuzu/discussion?'

params = {
    'start': 0
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
}

def get_proxy():
    # 蘑菇代理接口
    api_url = 'http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=4413430e0b224f59807475162ca1a4f4&count=20&expiryDate=0&format=1&newLine=2'
    r = requests.get(api_url, headers=headers)
    json_data = r.json()
    if type(json_data['msg']) == list:
        proxy_list = json_data['msg'][0]
        port = proxy_list['port']
        ip = proxy_list['ip']
        proxy = ip + ':' + port
        return proxy
    else:
        return None

def get_one_page(url):
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    if html:
        soup = BeautifulSoup(html, 'lxml')
        article_list = soup.find('table', class_='olt')
        for article in article_list.find_all('tr', class_=''):
            title = article.find('td', class_='title').a.get('href')
            author = article.find('td', nowrap=True, class_=False).a.string
            yield(title, author)
    else:
        soup = None
        print("No Pages!")


def get_img(url):
    r = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        img_list = soup.find('div', class_='image-wrapper').find_all('img')
    except:
        img_list = None
    if img_list != None:
        for img in img_list:
            img_url = img.get('src')
            yield(img_url)


def saveImg(img_url, dirname):
    r = requests.get(img_url, headers=headers, proxies=proxies)
    img_content = r.content
    try:
        with open('./img/'+dirname+'.jpg', 'wb') as f:
            f.write(img_content)
            f.close()
    except:
        pass


def main(offset):
    global proxies
    # 获取proxy
    proxy = get_proxy()
    if proxy == None:
        print('代理使用光了,没办法只能停下来了……')
        exit()
    
    proxies = {'https' : 'https://'+proxy}

    print("正在保存第"+str(offset+1)+"页")

    params['start'] = offset * 25
    url = baseUrl+parse.urlencode(params)
    html = get_one_page(url)
    for item in parse_one_page(html):
        title = item[0]
        author = item[1]
        img_list = get_img(title)
        for img_url in img_list:
            print("正在爬取作者："+author)
            saveImg(img_url, author)
    
    print("第"+str(offset+1)+"页保存完毕")


if __name__ == '__main__':
    for page in range(1000):
        try:
            main(page)
        except:
            continue