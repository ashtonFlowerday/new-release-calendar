import base64
import json
import re

from selenium import webdriver

import requests
from bs4 import BeautifulSoup
import datetime
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

today = datetime.date.today()

year = today.year

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

logger = logging.getLogger(__name__)

newReleases = []


class Book:
    author = []
    title = ""
    date = ""
    genre = ""
    tags = []
    pages = ""
    isbn = ""
    cover = ""
    synopsis = ""
    publisher = ""
    goodreads_link = ""
    amazon_link = ""

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
    additional_info=[]
    goodreads_link = ""
    amazon_link = ""

    def __init__(self,p,b,n):
        self.photo = p
        self.bio = b
        self.name = n


def author_goodreads_scrape(book):
    logger.info(str(datetime.datetime.now())+" "+"Goodreads author scrape")
    brave_path = "C:\\Program Files\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    option = webdriver.ChromeOptions()
    option.binary_location = brave_path
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--headless")
    option.add_argument("--disable-gpu")
    option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    browser = webdriver.Chrome(options=option)
    browser.get("https://www.goodreads.com/search?utf8=%E2%9C%93&query="+book.isbn)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    authors_links = soup.find(class_="ContributorLinksList").find_all("a")
    for i in range(0, len(authors_links)):
            author_browser = webdriver.Chrome(options=option)
            author_browser.get(authors_links[i]["href"])
            author_soup = BeautifulSoup(author_browser.page_source, 'html.parser')
            author_name = author_soup.find("h1", {"class": "authorName"}).find("span").get_text()
            author = next(author for author in book.author if author.name == author_name)
            if author!= None:
                int = book.author.index(author)
                bio = author_soup.find("div", {"class": "aboutAuthorInfo"}).find("span",{"style": "display:none"}).get_text()
                photo = author_soup.find("img", {"alt": author_name})["src"]
                if len(author.bio)<len(bio):
                    author.bio = bio
                if len(author.photo)<len(photo):
                    author.photo = photo
                additional_titles = author_soup.find_all("div", {"class": "dataTitle"})
                additional_items = author_soup.find_all("div", {"class": "dataItem"})
                for j in range(0, len(additional_titles)):
                    if "href" in additional_items[j]:
                        author.additional_info[j] = {additional_titles[j].get_text():additional_items[j].find("a")["href"]}
                    else:
                        author.additional_info[j] = {additional_titles[j].get_text():re.sub('<[^>]+>', '',additional_items[j].get_text().strip().strip("\n"))}
                book.author[int] = author
                return book
            else:
                bio = author_soup.find("div", {"class": "aboutAuthorInfo"}).find("span",{"style": "display:none"}).get_text()
                photo = author_soup.find("img", {"alt": author_name})["src"]
                additional_titles = author_soup.find_all("div", {"class": "dataTitle"})
                additional_items = author_soup.find_all("div", {"class": "dataItem"})
                a = Author(photo,bio,author_name)
                for j in range(0, len(additional_titles)):
                    if "href" in additional_items[j]:
                        print({additional_titles[j].get_text():additional_items[j].find("a")["href"]})
                        a.additional_info[j] = {additional_titles[j].get_text():additional_items[j].find("a")["href"]}
                    else:
                        print({additional_titles[j].get_text():re.sub('<[^>]+>', '',additional_items[j].get_text())})
                        a.additional_info[j] = {additional_titles[j].get_text():re.sub('<[^>]+>', '',additional_items[j].get_text().strip().strip("\n"))}
                book.author.append(a)
                print(book.author.__dict__)
                return book



    # except Exception as e:
    #     logger.error(e)
    #     return author_amazon_scrape(book)
    return book

# def author_amazon_scrape(book):
#     logger.info("Amazon author scrape")
#     brave_path = "C:\\Program Files\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
#     option = webdriver.ChromeOptions()
#     option.binary_location = brave_path
#     option.add_argument("--window-size=1920,1080")
#     option.add_argument("--headless")
#     option.add_argument("--disable-gpu")
#     option.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
#     browser = webdriver.Chrome(options=option)
#     browser.get("https://www.amazon.com/s?k="+book.isbn)
#     soup = BeautifulSoup(browser.page_source, 'html.parser')
#     print("https://www.amazon.com/s?k="+book.isbn)
#     print(soup)
#     try:
#         print(soup.find(class_="a-link-normal s-faceout-link a-text-normal"))
#         book_html=requests.get(soup.find(class_="a-link-normal s-faceout-link a-text-normal")["href"])
#         print(book_html)
#         book_soup = BeautifulSoup(book_html.content, 'html.parser')
#         author_links = book_soup.find_all(class_="bylineContributor")
#         authors = []
#         for i in author_links:
#             print(i)
#             author_html=requests.get(i["href"])
#             author_soup = BeautifulSoup(author_html.content, 'html.parser')
#             author_html = requests.get(author_soup.select_one('[data-testid="product-brand"]')["href"])
#             author_soup = BeautifulSoup(author_html.content, 'html.parser')
#             image = base64.b64encode(requests.get(author_soup.find(class_="AuthorBio__author-bio__author-picture__hz4cs").find("img")["href"]).content).decode("utf-8")
#             authors.append(Author(image, author_soup.find(class_="AuthorBio__author-bio__author-biography__WeqwH").get_text(),author_soup.find(class_="AuthorSubHeader__author-subheader__name__HkJyX").get_text()))
#
#         book.author = authors
#     except Exception as e:
#         logger.error(e)
#return book

def author_google_books_scrape(book, id):
    logger.info(str(datetime.datetime.now())+" "+"Google Books author scrape")
    brave_path = "C:\\Program Files\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    option = webdriver.ChromeOptions()
    option.binary_location = brave_path
    option.add_argument("--headless")
    browser = webdriver.Chrome(options=option)
    browser.get("https://www.google.co.za/books/edition/_/"+id+"?hl=en&gbpv=0")
    soup = BeautifulSoup(browser.page_source, 'html.parser')

    author_names = soup.find_all(class_ = "U7rXJc")
    author_bios = soup.find_all(class_ = "qO5zb")
    author_photos = soup.find_all(class_="IXgIFd")
    authors = []

    for i in range(0,len(author_names)):
            image = ""
            author_bio = ""
            try:
                logger.info(str(datetime.datetime.now())+" "+"Attempting to get author image")
                image = base64.b64encode(requests.get("https://www.google.co.za"+author_photos[i].find("a")["href"]).content).decode("utf-8")
            except Exception as e:
                logger.error(str(datetime.datetime.now())+" "+str(e))
            try:
                logger.info("Attempting to get author bio")
                author_bio = author_bios[i].get_text()
            except Exception as e:
                logger.error(str(datetime.datetime.now())+" "+str(e))
            authors.append(Author(image,author_bio,author_names[i].get_text()))

    book.author = authors
    return book

def google_books_api(book):
    try:
        book_details = json.loads(requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+book.isbn).text)
        book.date = book_details["items"][0]["volumeInfo"]["publishedDate"]
        book.publisher = book_details["items"][0]["volumeInfo"]["publisher"]
        for i in list(book_details["items"][0]["volumeInfo"]["categories"]):
            book.tags.append(i)
    except Exception as e:
        logger.error(str(datetime.datetime.now())+" "+str(e))
    book = author_google_books_scrape(book,book_details["items"][0]["id"])
    book = author_goodreads_scrape(book)
    return book

def get_books_for_the_month(month):
    pageNumber = 1
    html = requests.get("https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
        year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(pageNumber) + "&sort=x")
    soup = BeautifulSoup(html.content, 'html.parser')
    results = soup.find_all(attrs={'class': 'page-link'})
    pageNumber = int(results.__getitem__(len(results) - 2).get_text())

    logger.info(str(datetime.datetime.now())+" "+month+" "+str(year)+" has "+str(pageNumber)+" pages of new releases")

    for i in range(1, pageNumber + 1):
        logger.info(str(datetime.datetime.now())+" "+"Scraping year and month: "+month+" "+str(year))
        logger.info(str(datetime.datetime.now())+" "+"Scraping page: "+str(i))

        html = requests.get("https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
            year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(i) + "&sort=x")
        soup = BeautifulSoup(html.content, 'html.parser')
        table = soup.find(attrs={'id': 'srtauthlist'})
        books = table.find_all("tr")

        logger.info(str(datetime.datetime.now())+" "+"Scraping of book table complete!")

        for b in books:
            try:
                headers = {'Cookie': 'fdbid=284863; fdbunm=thevhssideshow; fdblvl=0; PHPSESSID=eiitv91qsbjaa4l9dmmj5j4k17'}

                book_html = requests.get("https://www.fictiondb.com"+(b.find("a", itemprop="url")['href']).replace("..",""), headers = headers)
                book_soup = BeautifulSoup(book_html.content, 'html.parser')
                image_url = book_soup.find("meta", property="og:image")["content"]


                logger.info(str(datetime.datetime.now())+" "+"Getting cover image of book")
                try:
                    if "NoCover" in image_url:
                        logger.warning(str(datetime.datetime.now())+" "+"No cover found!")
                        cover_image = ""
                    else:
                        cover_image = base64.b64encode(requests.get(image_url).content).decode("utf-8")
                except:
                    logger.error(str(datetime.datetime.now())+" "+"Something went wrong with the book cover!")
                    cover_image = ""


                try:
                    logger.info(str(datetime.datetime.now())+" "+"Getting number of pages of book")
                    pages = book_soup.find(string="Pages:").findParent("li").find("div").get_text().strip()
                except:
                    logger.warning(str(datetime.datetime.now())+" "+"No number of pages found!")
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
                logger.error(str(datetime.datetime.now())+" "+str(e))



logging.basicConfig(filename='webscraper.log', level=logging.INFO)


for m in months:
    get_books_for_the_month(m)

# x = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:9798891321045")
# print(x.text)