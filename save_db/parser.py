import re  # use Regular expression.
import requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import numpy as np
from multiprocessing import Pool
import pymysql
import schedule
import time


conn = pymysql.connect(
    user='news_usr',
    passwd='0607',
    host='localhost',
    db='news_data',
    charset='utf8'
)


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/3.12.129.46 Safari/537.36"}
df_headers = ["title", "link", "contents", "section"]  # dataframe header
df_main = pd.DataFrame(columns=df_headers)


def get_content_data(link):
    try:
        content_url = link

        res = requests.get(content_url, headers=headers)
        res.raise_for_status()
        content_html = urllib.request.urlopen(content_url).read()
        soup = BeautifulSoup(content_html, "html.parser")
        return soup.select_one("#articleBodyContents").get_text()

    except AttributeError as e:
        return ""  # if contents is "None", then return ""


def get_news_section(link):
    try:
        content_url = link

        res = requests.get(content_url, headers=headers)
        res.raise_for_status()
        content_html = urllib.request.urlopen(content_url).read()
        soup = BeautifulSoup(content_html, "html.parser")
        # sections = soup("em", attrs={"class": "guide_categorization_item"})
        section = soup.select_one(".guide_categorization_item").get_text()
        return section

    except AttributeError as e:
        return ""  # if contents is "None", then return ""


def save_data(tags, df):
    for tag in tags:
        link = tag.get('href', None)
        title = tag.get_text()
        content_data = get_content_data(link)
        section = get_news_section(link)
        df_s = pd.DataFrame({'title': [title], 'link': [link], 'contents': [content_data], 'section': [section]})
        df = pd.concat([df, df_s])

    df = df.drop_duplicates(["link"])
    df["contents"].replace("", np.nan, inplace=True)
    df = df[df["contents"].notna()]

    return df


def parse_news():
    main_url = "https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&sid1=001&sid2=140&oid=001&isYeonhapFlash=Y"
    res = requests.get(main_url, headers=headers)
    res.raise_for_status()
    main_html = urllib.request.urlopen(main_url).read()
    soup = BeautifulSoup(main_html, "html.parser")  # main first page
    news_pages = soup("a", attrs={"class": "nclicks(fls.page)"})  # next pages link

    # first page scraping
    tags1 = soup("a", attrs={"class": re.compile("nclicks\(fls.list\)")})  # upper part of the news
    tags2 = soup("a", attrs={"class": re.compile("nclicks\(cnt_flashart\)")})  # lower part the news
    global df_main
    df_main = save_data(tags1, df_main)
    df_main = save_data(tags2, df_main)

    # scrap the rest of the pages
    for page in news_pages:
        page_url = "https://news.naver.com/main/list.naver" + page.get('href', None)
        res = requests.get(page_url, headers=headers)
        res.raise_for_status()
        page_html = urllib.request.urlopen(page_url).read()
        soup = BeautifulSoup(page_html, "html.parser")
        page_tag = soup("a", attrs={"class": re.compile("nclicks\(cnt_flashart\)")})

        df_main = save_data(page_tag, df_main)

    return df_main


# if __name__ == '__main__':
#     news_data_df = parse_news()
#     news_data_df.reset_index(inplace=True)
#     cursor = conn.cursor()
#
#     sql = "INSERT INTO news (title, link, contents, section) VALUES (%s, %s, %s, %s)"
#
#     for i in news_data_df.index:
#         n_title = news_data_df['title'][i]
#         n_link = news_data_df['link'][i]
#         n_contents = news_data_df['contents'][i]
#         n_section = news_data_df['section'][i]
#
#         val = (n_title, n_link, n_contents, n_section)
#         cursor.execute(sql, val)
#
#         conn.commit()


def main():
    news_data_df = parse_news()
    news_data_df.reset_index(inplace=True)
    cursor = conn.cursor()

    sql = "INSERT INTO news (title, link, contents, section) VALUES (%s, %s, %s, %s)"

    for i in news_data_df.index:
        n_title = news_data_df['title'][i]
        n_link = news_data_df['link'][i]
        n_contents = news_data_df['contents'][i]
        n_section = news_data_df['section'][i]

        val = (n_title, n_link, n_contents, n_section)
        cursor.execute(sql, val)

        conn.commit()


schedule.every().day.at("22:30").do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
