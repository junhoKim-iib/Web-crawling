#Dataset format : [title, link, contents,token]
import re  # use Regular expression.
import requests
from bs4 import BeautifulSoup
import urllib
from datetime import datetime,timedelta #get today's date.
import pandas as pd 
import numpy as np
from konlpy.tag import * # using Okt now
from gensim.models.doc2vec import Doc2Vec
import os


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/3.12.129.46 Safari/537.36"}
df_headers = ["title","link","contents","Token"]

okt = Okt()

#open stopwords.txt file.
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
        return "" # if contents is "None", then remove from .xlsx file


def save_data(tags):
    for tag in tags:
        link = tag.get('href',None)
        title = tag.get_text()
        
        content_data = get_content_data(link) 
        token_data = okt.nouns(content_data)
        stopwords_token = []
        for word in token_data:
            if word not in stop_words:
                stopwords_token.append(word)

        news_data.append([title,link,content_data,stopwords_token])
    df = pd.DataFrame(news_data,columns=df_headers) 
  
    df = df.drop_duplicates(["link"])
    df["contents"].replace("",np.nan,inplace=True)
    df = df[df["contents"].notna()]
    

    


    if not os.path.exists('Naver_news.xlsx'):
        df.to_excel("Naver_news.xlsx",sheet_name="Naver_news",index=False)

    else:
       with pd.ExcelWriter('Naver_news.xlsx', engine='openpyxl', mode='a',if_sheet_exists='overlay') as writer: 
        df.to_excel(writer,sheet_name="Naver_news",startrow=writer.sheets["Naver_news"].max_row,header=False,index=False) 



today = datetime.today()
start_date = today - timedelta(days=30)


while start_date<=today:

    print("date : {}".format(start_date))
    date = start_date.strftime("%Y%m%d")
    #make pandas data frame
    news_data = []
    last_page = 10
    for i in range(1,last_page+1): #loop for each pages.
        print("page : ",i)
        url = "https://news.naver.com/main/list.naver?mode=LPOD&sid2=140&sid1=001&mid=sec&oid=001&isYeonhapFlash=Y&date={}&page={}".format(date,i) #Breaking news from Yonhap News page.
        res = requests.get(url,headers=headers)
        res.raise_for_status()

        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html,"html.parser")
        tags1 = soup("a",attrs={"class":re.compile("nclicks\(fls.list\)")}) # Top of the news
        tags2 = soup("a",attrs={"class":re.compile("nclicks\(cnt_flashart\)")}) # Bottom of the news

        save_data(tags1)
        save_data(tags2)

    start_date += timedelta(days =1)


#Save data as a excel file.


#df = pd.DataFrame(news_data,columns=df_headers) 

#df["contents"].replace("",np.nan,inplace=True)
#df = df[df["contents"].notna()]
#df.to_excel("Naver_news.xlsx",index=False)


#apart = pd.read_excel("Naver_news.xlsx",sheet_name="Sheet1")
#df = apart.drop_duplicates(["link"]) #Delete duplicate data.

#df.to_excel("Naver_news.xlsx",sheet_name="Naver_news",index=False)