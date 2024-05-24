import base64
import concurrent.futures
import urllib

import requests
from bs4 import BeautifulSoup
import datetime

today = datetime.date.today()

year = today.year

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

newReleases = []


class Book:
    author = ""
    title = ""
    date = ""
    genre = ""
    tags = []
    pages = ""
    isbn = ""
    cover = ""
    synopsis = ""

    def __init__(self, a, t, d, g, s, i, c, ts, p):
        a = a.split(",")
        self.author = a
        self.title = t
        self.date = d
        self.genre = g
        self.synopsis = s
        self.isbn = i
        self.cover = c
        self.tags = ts
        self.pages = p



def getBooksForTheMonth(month):
    pageNumber = 1
    url = "https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
        year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(pageNumber) + "&sort=x"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    results = soup.find_all(attrs={'class': 'page-link'})
    pageNumber = int(results.__getitem__(len(results) - 2).get_text())
    print("/////////////////////" + month + " " + str(pageNumber) + "/////////////////////")
    for i in range(1, pageNumber + 1):
        print("**********************" + month + " " + str(i) + "*******************")
        url = "https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
            year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(i) + "&sort=x"
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        table = soup.find(attrs={'id': 'srtauthlist'})
        books = table.find_all("tr")
        for b in books:
            try:
                headers = {'Cookie': 'fdbid=284863; fdbunm=thevhssideshow; fdblvl=0; PHPSESSID=eiitv91qsbjaa4l9dmmj5j4k17'}

                book_html = requests.get("https://www.fictiondb.com"+(b.find("a", itemprop="url")['href']).replace("..",""), headers = headers)
                book_soup = BeautifulSoup(book_html.content, 'html.parser')
                image_url = book_soup.find("meta", property="og:image")["content"]

                if "NoCover" in image_url:
                    image = ""
                else:
                    image = base64.b64encode(requests.get(image_url).content).decode("utf-8")

                try:
                    page = book_soup.find(string="Pages:").findParent("li").find("div").get_text().strip()
                except:
                    page = ""

                book = Book(b.find("a", itemprop = 'author').get_text(),
                            b.find("span", itemprop = 'name').get_text(),
                            b.find("span", itemprop = 'datePublished').get_text(),
                            b.find("span", itemprop = 'genre').get_text().strip().strip("/").strip(),
                            book_soup.find("div",id="description").get_text().strip(),
                            book_soup.find("meta", property="book:isbn")["content"],
                            image,
                            [g.get_text() for g in book_soup.find("div",class_="col-sm-4 col-md-4").find_all("a")],
                            page)

                print(book.__dict__)
                newReleases.append(book)
            except Exception as e:
                print(e)

for m in months:
    getBooksForTheMonth(m)