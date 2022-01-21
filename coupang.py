from email import header
from attr import attrs
from bcrypt import re
import requests
from bs4 import BeautifulSoup


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/3.12.129.46 Safari/537.36"}
for i in range(1,6):
    print("page : ",i)
    url = "https://www.coupang.com/np/search?q=%EB%85%B8%ED%8A%B8%EB%B6%81&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=36&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page={}&rocketAll=false&searchIndexingToken=1=5&backgroundColor=".format(i)
    res = requests.get(url,headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text,"lxml")

    items = soup.find_all("li",attrs={"class":re.compile("^search-product")})
    #print(items[0].find("div",attrs={"class":"name"}).get_text())
    for item in items:
        ad_badge = item.find("span",attrs={"class":"ad-badge-text"}) #ad products are excluded.
        if ad_badge:
            #print("<Skip an ad item.>")
            continue

        name = item.find("div",attrs={"class":"name"}).get_text()
        price = item.find("strong",attrs={"class":"price-value"}).get_text()
        
        # Only search products with more than 100 reviews and 4.5 ratings.
        rate = item.find("em",attrs={"class":"rating"})
        if rate:
            rate = rate.get_text()
            rating_cnt = item.find("span",attrs={"class":"rating-total-count"})
            rating_cnt = rating_cnt.get_text()
            rating_cnt = rating_cnt[1:-1] # Remove parenthesis. ex) (97) --> 97
        else: # if there is no rate
            rate = "Skip the no rate product"
            rating_cnt = "0"
            continue

        link = item.find("a",attrs={"class":"search-product-link"})["href"]

        if float(rate) >= 4.5 and int(rating_cnt)>=100:
            print(f"Product Name : {name}")
            print(f"Price : {price}")
            print(f"Rate : {rate}, {rating_cnt} reviews")
            print("Link : {}".format("https://www.coupang.com"+link))
            print("-"*90)