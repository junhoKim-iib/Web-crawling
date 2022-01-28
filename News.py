from email import header
from attr import attrs
from bcrypt import re
import requests
from bs4 import BeautifulSoup
import urllib
from datetime import datetime
import pandas as pd
from sqlalchemy import false, true

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/3.12.129.46 Safari/537.36"}
date = datetime.today().strftime("%Y%m%d") # today's date

count = 0 # count news 
print("date : {}".format(date))

#make pandas data frame
news_data = []

for i in range(1,15): #loop for each pages 
    print("page : ",i)
    url = "https://news.naver.com/main/list.naver?mode=LPOD&sid2=140&sid1=001&mid=sec&oid=001&isYeonhapFlash=Y&date={}&page={}".format(date,i) #Breaking news from Yonhap News page.
    res = requests.get(url,headers=headers)
    res.raise_for_status()

    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,"html.parser")
    tags1 = soup("a",attrs={"class":re.compile("nclicks\(fls.list\)")}) # Top of the news
    tags2 = soup("a",attrs={"class":re.compile("nclicks\(cnt_flashart\)")}) # Bottom of the news

    for tag in tags1:
        link = tag.get('href',None)
        title = tag.get_text()
        news_data.append([title,link])
        count += 1

    for tag in tags2:
        link = tag.get('href',None)
        title = tag.get_text()
        news_data.append([title,link])
        count += 1
    
    print("count :{} ".format(count))

df = pd.DataFrame(news_data,columns=["title","link"]) 
df.to_excel("Naver_news.xlsx",index=False)

apart = pd.read_excel("Naver_news.xlsx",sheet_name="Sheet1")
df = apart.drop_duplicates(["title","link"])

df.to_excel("Naver_news.xlsx",sheet_name="Naver_news",index=False)