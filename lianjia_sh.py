import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent

def getHtmlText(url):
    try:
        ua=UserAgent()
        headers={'User-Agent':ua.random}
        r=requests.get(url,headers=headers,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ""

def getDetails(url):
    detail={}
    html=getHtmlText(url)
    soup=BeautifulSoup(html,'html.parser')
    b=soup.find("div",class_="content zf-content")
    detail['月租金']=int(b.find("span",class_="total").text.strip())
    detail['面积']=b.find_all("p",class_="lf")[0].text[3:].strip()
    detail['房屋户型']=b.find_all("p",class_="lf")[1].text[5:].strip()
    detail['楼层']=b.find_all("p",class_="lf")[2].text[3:].strip()
    detail['房屋朝向']=b.find_all("p",class_="lf")[3].text[5:].strip()
    detail['地铁']=b.find_all("p")[4].text[3:].strip().strip()
    detail['小区']=b.find_all("p")[5].text[3:].strip()
    detail['位置']=b.find_all("p")[6].text[3:].strip()
    return detail

def get_link(pages,L):
    try:
        num=int(pages)+1
        for i in range(1,num):
            url='https://sh.lianjia.com/zufang/pg'+str(i)+'/'
            soup = BeautifulSoup(getHtmlText(url),'html.parser')
            a=soup.find_all("div",class_="info-panel")
            for j in range(len(a)):
                try:
                    link=a[j].find("a")["href"]
                    print (link)
                    L.append(getDetails(link))
                    print ('Page',i,'-',j,' done.')
                except:
                    print ('Page',i,'-',j,' has issues.')
                    continue
    except:
        return ''
    finally:
        return L


def main():
    pages=input('请输入您需要下载的页数：')
    result=[]
    data=pd.DataFrame(get_link(pages,result)) #把装着数据的house_result（list容器）转换为数据框（表格化数据）
    data.to_csv('链家网租房数据.csv',encoding='utf_8_sig') #

if __name__=='__main__':
    main()

