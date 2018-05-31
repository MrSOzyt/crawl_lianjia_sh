from threading import Thread
import threading
from queue import Queue
import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import time

def run_time(func):
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        end = time.time()
        print('running', end-start, 's')
    return wrapper


class Spider():
    def __init__(self):
        self.q = Queue()
        self.data = []
        self.page_num = 10
        self.thread_num = 10
        self.headers={'User-Agent':UserAgent().random}

    def produce_url(self):
        baseurl = 'https://sh.lianjia.com/zufang/pg{}'
        L=[]
        for i in range(1, self.page_num + 1):
            page_url = baseurl.format(i)
            L.append(page_url)
            for j in L:
                try:
                    r=requests.get(j,headers=self.headers,timeout=30)
                    r.raise_for_status()
                    r.encoding=r.apparent_encoding
                    soup = BeautifulSoup(r.text,'html.parser')
                    a=soup.find_all("div",class_="info-panel")
                    for k in range(len(a)):
                            link=a[j].find("a")["href"]
                            self.q.put(link)
                except:
                    continue

    def get_info(self):
        while not self.q.empty():
            url = self.q.get()
            print('crawling', url)
            req = requests.get(url, headers=self.headers)
            soup=BeautifulSoup(req.text,'html.parser')
            b=soup.find("div",class_="content zf-content")
            detail={}
            detail['月租金']=int(b.find("span",class_="total").text.strip())
            detail['面积']=b.find_all("p",class_="lf")[0].text[3:].strip()
            detail['房屋户型']=b.find_all("p",class_="lf")[1].text[5:].strip()
            detail['楼层']=b.find_all("p",class_="lf")[2].text[3:].strip()
            detail['房屋朝向']=b.find_all("p",class_="lf")[3].text[5:].strip()
            detail['地铁']=b.find_all("p")[4].text[3:].strip().strip()
            detail['小区']=b.find_all("p")[5].text[3:].strip()
            detail['位置']=b.find_all("p")[6].text[3:].strip()

            self.data.append(detail)

    @run_time
    def run(self):
        self.produce_url()
        ths = []
        for _ in range(self.thread_num):
            th = Thread(target=self.get_info)
            th.start()
            ths.append(th)
        for th in ths:
            th.join()
        data=pd.DataFrame(self.data)
        data.to_csv('链家网租房数据.csv',encoding='utf_8_sig')
        print('Data crawling is finished.')

if __name__ == '__main__':
    Spider().run()



