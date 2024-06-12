import base64
import json

from pymongo import MongoClient
from selenium import webdriver

import requests
from bs4 import BeautifulSoup
import datetime
import logging
import pymongo
import traceback

logger = logging.getLogger(__name__)

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
    personal_website = ""
    goodreads_link = ""

    def __init__(self, p,b,n):
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
            author = None
            try:
                author = next(author for author in book.author if author.name == author_name)
            except Exception as e:
                logger.error(datetime.datetime.now()+" "+str(e)+"\n"+traceback.format_exc())
            if author!= None:
                int = book.author.index(author)
                bio = ""
                photo = ""
                try:
                    bio = author_soup.find("div", {"class": "aboutAuthorInfo"}).find("span",{"style": "display:none"}).get_text()
                except Exception as e:
                    logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
                try:
                    photo = author_soup.find("img", {"alt": author_name})["src"]
                except Exception as e:
                    logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
                if len(author.bio)<len(bio):
                    logger.info("New author bio added")
                    author.bio = bio
                if len(author.photo)<len(photo) and "nophoto" not in photo:
                    logger.info("New author photo added")
                    author.photo = base64.b64encode(requests.get(photo).content).decode("utf-8")
                try:
                    websites = author_soup.find_all("a", {"itemprop": "url"})
                    for j in range(0, len(websites)):
                        if "twitter" and "instagram" and "goodreads" not in websites[j]["href"] and "http" in websites[j]["href"]:
                            author.personal_website = websites[j]["href"]
                except Exception as e:
                    logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
                author.goodreads_link = authors_links[i]["href"]
                book.author[int] = author
            else:
                bio = ""
                photo = ""
                try:
                    bio = author_soup.find("div", {"class": "aboutAuthorInfo"}).find("span",{"style": "display:none"}).get_text()
                except Exception as e:
                    logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
                try:
                    if "nophoto" not in author_soup.find("img", {"alt": author_name})["src"]:
                        photo = base64.b64encode(requests.get(author_soup.find("img", {"alt": author_name})["src"]).content).decode("utf-8")
                except Exception as e:
                    logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
                a = Author(photo,bio,author_name)
                try:
                    websites = author_soup.find_all("a", {"itemprop": "url"})
                    for j in range(0, len(websites)):
                        if "twitter" and "instagram" and "goodreads" not in websites[j]["href"] and "http" in websites[j]["href"]:
                            a.personal_website = websites[j]["href"]
                except Exception as e:
                    logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
                a.goodreads_link = authors_links[i]["href"]
                book.author.append(a)
    print(book.__dict__)
    for i in book.author:
        print(i.__dict__)
    return book

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
                logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
            try:
                logger.info("Attempting to get author bio")
                author_bio = author_bios[i].get_text()
            except Exception as e:
                logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
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
        logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())
    book = author_google_books_scrape(book,book_details["items"][0]["id"])
    book = author_goodreads_scrape(book)
    return book

def get_books_for_the_month(month, year):
    newReleasesForMonth = []
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
                        logger.warning(str(datetime.datetime.now())+" "+"No cover found!"+"\n"+traceback.format_exc())
                        cover_image = ""
                    else:
                        cover_image = base64.b64encode(requests.get(image_url).content).decode("utf-8")
                except:
                    logger.error(str(datetime.datetime.now())+" "+"Something went wrong with the book cover!"+"\n"+traceback.format_exc())
                    cover_image = ""


                try:
                    logger.info(str(datetime.datetime.now())+" "+"Getting number of pages of book")
                    pages = book_soup.find(string="Pages:").findParent("li").find("div").get_text().strip()
                except:
                    logger.warning(str(datetime.datetime.now())+" "+"No number of pages found!"+"\n"+traceback.format_exc())
                    pages = ""


                book = Book(b.find("a", itemprop = 'author').get_text(),
                            b.find("span", itemprop = 'name').get_text(),
                            b.find("span", itemprop = 'genre').get_text().strip().strip("/").strip(),
                            book_soup.find("div",id="description").get_text().strip(),
                            book_soup.find("meta", property="book:isbn")["content"],
                            cover_image,
                            [g.get_text() for g in book_soup.find("div",class_="col-sm-4 col-md-4").find_all("a")],
                            pages)

                book.goodreads_link = "https://www.goodreads.com/search?utf8=%E2%9C%93&query="+book.isbn
                book.amazon_link = "https://www.amazon.com/s?k="+book.isbn

                book = google_books_api(book)

                newReleasesForMonth.append(book)

            except Exception as e:
                logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())

    return newReleasesForMonth



logging.basicConfig(filename='webscraper.log', level=logging.INFO)

today = datetime.date.today()

year = today.year

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


uri = "mongodb+srv://Novel2:p6TWcjjuSwxtkVz4@novel2.8fpednf.mongodb.net/?retryWrites=true&w=majority&appName=Novel2"

client = MongoClient(uri)

for y in range(0, 3):
    for m in months:
        booksForMonth = get_books_for_the_month(m, year+y)
        bookCollection = client.get_database("Novel2").get_collection("book")
        authorCollection = client.get_database("Novel2").get_collection("author")
        try:
            bookCollection.insert_many(booksForMonth)
            for b in booksForMonth:
                authorCollection.insert_many(b.author)
        except Exception as e:
            logger.error(str(datetime.datetime.now())+" "+str(e)+"\n"+traceback.format_exc())

