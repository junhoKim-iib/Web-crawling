# Dataset format : [title, link, contents,token]
import re  # use Regular expression.
import requests
from bs4 import BeautifulSoup
import urllib
from datetime import datetime  # get today's date.
import pandas as pd  # for dataframe
from konlpy.tag import *
from gensim.models.doc2vec import Doc2Vec

okt = Okt()
stop_words_f = open("stopwords.txt", "r", encoding="utf-8")
stop_words = stop_words_f.read()
stop_words_f.close()

stop_words = stop_words.split(" ")


def get_content_data(link):
    
    content_url = link

    res = requests.get(content_url, headers=headers)
    res.raise_for_status()
    content_html = urllib.request.urlopen(content_url).read()
    soup = BeautifulSoup(content_html, "html.parser")

    contents = soup.select_one("#articleBodyContents")
    if contents == None:
        return ""
    else :
        return contents.get_text()

def add_data(tag):
    # add row datas 
    return tag


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/3.12.129.46 Safari/537.36"}
date = datetime.today().strftime("%Y%m%d") # today's date

count = 0  # count news
print("date : {}".format(date))

# make pandas data frame
news_data = []
last_page = 2
for i in range(1,last_page+1): # loop for each pages.
    print("page : ", i, "  date : ", date, "  page : ", i)
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&listType=paper&sid1=001&date={}&page={}".format(date,i) #Breaking news from Yonhap News page.
    res = requests.get(url,headers=headers)
    res.raise_for_status()

    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,"html.parser")
    tags = soup.find_all("li")
    print(tags)


    for tag in tags:
        link = tag.get('href')
        title = tag.get_text()
        
        content_data = get_content_data(link) 
        token_data = okt.nouns(content_data)  # tokenize data by okt.
        stopwords_token = []
        for word in token_data:
            if word not in stop_words:
                stopwords_token.append(word)
        news_data.append([title, link, content_data, stopwords_token])
       
        count += 1
    
    print("count :{} ".format(count))


# Save data as a excel file.
headers = ["title", "link", "contents", "Token"]

df = pd.DataFrame(news_data, columns=headers)
df.to_excel("Naver_news.xlsx", index=False)


apart = pd.read_excel("Naver_news.xlsx", sheet_name="Sheet1")
df = apart.drop_duplicates(["link"])  # Delete duplicate data.

df.to_excel("Naver_news.xlsx", sheet_name="Naver_news", index=False)

