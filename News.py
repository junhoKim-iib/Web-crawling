#Dataset format : [title, link, contents,token,vector]
import re  # use Regular expression.
import requests
from bs4 import BeautifulSoup
import urllib
from datetime import datetime #get today's date.
import pandas as pd # for dataframe
from konlpy.tag import *
from gensim.models.doc2vec import Doc2Vec


okt = Okt()
stop_words_f = open("stopwords.txt","r",encoding="utf-8")
stop_words = stop_words_f.read()
stop_words_f.close()

stop_words = stop_words.split(" ")


def get_content_data(link):
    try:
        content_url = link
    
        res = requests.get(content_url,headers=headers)
        res.raise_for_status()
        content_html = urllib.request.urlopen(content_url).read()
        soup = BeautifulSoup(content_html,"html.parser")
        return soup.select_one("#articleBodyContents").get_text()
    
    except AttributeError as e:
        return soup.select_one("#newsEndContents").get_text()


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/3.12.129.46 Safari/537.36"}
date = datetime.today().strftime("%Y%m%d") # today's date

count = 0 # count news 
print("date : {}".format(date))

#make pandas data frame
news_data = []
last_page = 2
for i in range(1,last_page+1): #loop for each pages.
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
        
        content_data = get_content_data(link) 
        token_data = okt.nouns(content_data)
        stopwords_token = []
        for word in token_data:
            if word not in stop_words:
                stopwords_token.append(word)
        news_data.append([title,link,content_data,stopwords_token])
       
        count += 1


    for tag in tags2:
        link = tag.get('href',None)
        title = tag.get_text()

        content_data = get_content_data(link)
        token_data = okt.nouns(content_data)
        stopwords_token = []
        for word in token_data:
            if word not in stop_words:
                stopwords_token.append(word)

        news_data.append([title,link,content_data,stopwords_token])

        count += 1
    
    print("count :{} ".format(count))


#Save data as a excel file.
headers = ["title","link","contents","Token"]

df = pd.DataFrame(news_data,columns=headers) 
df.to_excel("Naver_news.xlsx",index=False)


apart = pd.read_excel("Naver_news.xlsx",sheet_name="Sheet1")
df = apart.drop_duplicates(["link"]) #Delete duplicate data.

df.to_excel("Naver_news.xlsx",sheet_name="Naver_news",index=False)

