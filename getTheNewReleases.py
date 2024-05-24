import base64
import json

import requests
from bs4 import BeautifulSoup
import datetime
import logging

today = datetime.date.today()

year = today.year

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

logger = logging.getLogger(__name__)

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
    publisher = ""
    id = ""

    def __init__(self, a, t, g, s, i, c, ts, p):
        self.author = a
        self.title = t
        self.genre = g
        self.synopsis = s
        self.isbn = i
        self.cover = c
        self.tags = ts
        self.pages = p

class Author:
    photo = ""
    bio = ""
    name = ""
    id = ""
def goodreads_scrape(book):
    html = requests.get("https://www.goodreads.com/search?q="+book.isbn)
    soup = BeautifulSoup(html.content, 'html.parser')

    return book

def amazon_scrape(book):
    return book

def google_books_api(book):
    book_details = json.loads(requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+book.isbn).text)
    book.date = book_details["items"][0]["volumeInfo"]["publishedDate"]
    book.publisher = book_details["items"][0]["volumeInfo"]["publisher"]
    for i in book_details["items"][0]["volumeInfo"]["categories"]:
        book.tags.append(i)
    return book

def get_books_for_the_month(month):
    pageNumber = 1
    html = requests.get("https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
        year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(pageNumber) + "&sort=x")
    soup = BeautifulSoup(html.content, 'html.parser')
    results = soup.find_all(attrs={'class': 'page-link'})
    pageNumber = int(results.__getitem__(len(results) - 2).get_text())

    logger.info(month+" "+str(year)+" has "+str(pageNumber)+" pages of new releases")

    for i in range(1, pageNumber + 1):
        logger.info("Scraping year and month: "+month+" "+str(year))
        logger.info("Scraping page: "+str(i))

        html = requests.get("https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
            year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(i) + "&sort=x")
        soup = BeautifulSoup(html.content, 'html.parser')
        table = soup.find(attrs={'id': 'srtauthlist'})
        books = table.find_all("tr")

        logger.info("Scraping of book table complete!")

        for b in books:
            try:
                headers = {'Cookie': 'fdbid=284863; fdbunm=thevhssideshow; fdblvl=0; PHPSESSID=eiitv91qsbjaa4l9dmmj5j4k17'}

                book_html = requests.get("https://www.fictiondb.com"+(b.find("a", itemprop="url")['href']).replace("..",""), headers = headers)
                book_soup = BeautifulSoup(book_html.content, 'html.parser')
                image_url = book_soup.find("meta", property="og:image")["content"]


                logger.info("Getting cover image of book")
                try:
                    if "NoCover" in image_url:
                        logger.warning("No cover found!")
                        cover_image = ""
                    else:
                        cover_image = base64.b64encode(requests.get(image_url).content).decode("utf-8")
                except:
                    logger.error("Something went wrong with the book cover!")
                    cover_image = ""


                try:
                    logger.info("Getting number of pages of book")
                    pages = book_soup.find(string="Pages:").findParent("li").find("div").get_text().strip()
                except:
                    logger.warning("No number of pages found!")
                    pages = ""


                book = Book(b.find("a", itemprop = 'author').get_text(),
                            b.find("span", itemprop = 'name').get_text(),
                            b.find("span", itemprop = 'genre').get_text().strip().strip("/").strip(),
                            book_soup.find("div",id="description").get_text().strip(),
                            book_soup.find("meta", property="book:isbn")["content"],
                            cover_image,
                            [g.get_text() for g in book_soup.find("div",class_="col-sm-4 col-md-4").find_all("a")],
                            pages)

                book = google_books_api(book)

                newReleases.append(book)

            except Exception as e:
                logger.error(e)



logging.basicConfig(filename='webscraper.log', level=logging.INFO)

for m in months:
    get_books_for_the_month(m)

# x = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:9798891321045")
# print(x.text)