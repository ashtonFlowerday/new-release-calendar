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

uri = "mongodb+srv://Novel2:p6TWcjjuSwxtkVz4@novel2.8fpednf.mongodb.net/?retryWrites=true&w=majority&appName=Novel2"

client = MongoClient(uri)

author_list = []
book_list = []

bookCollection = client.get_database("Novel2").get_collection("book")
authorCollection = client.get_database("Novel2").get_collection("author")


class Book:
    _id = ""
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

class Author:
    _id = ""
    photo = ""
    bio = ""
    name = ""
    personal_website = ""
    twitter = ""
    instagram = ""
    goodreads_link = ""

    def __init__(self, p, b, n):
        self.photo = p
        self.bio = b
        self.name = n


def author_goodreads_scrape(book):
    logger.info(str(datetime.datetime.now()) + " " + "Goodreads author scrape")
    brave_path = "C:\\Program Files\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    option = webdriver.ChromeOptions()
    option.binary_location = brave_path
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--headless")
    option.add_argument("--disable-gpu")
    option.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    browser = webdriver.Chrome(options=option)
    browser.get("https://www.goodreads.com/search?utf8=%E2%9C%93&query=" + book.isbn)
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
            print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
        if author != None:
            int = book.author.index(author)
            bio = ""
            photo = ""
            try:
                bio = author_soup.find("div", {"class": "aboutAuthorInfo"}).find("span",
                                                                                 {"style": "display:none"}).get_text()
            except Exception as e:
                print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            try:
                photo = author_soup.find("img", {"alt": author_name})["src"]
            except Exception as e:
                print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            if len(author.bio) < len(bio):
                logger.info("New author bio added")
                author.bio = bio
            if len(author.photo) < len(photo) and "nophoto" not in photo:
                logger.info("New author photo added")
                author.photo = base64.b64encode(requests.get(photo).content).decode("utf-8")
            try:
                websites = author_soup.find_all("a", {"itemprop": "url"})
                for j in range(0, len(websites)):
                    if "twitter" and "instagram" and "goodreads" not in websites[j]["href"] and "http" in websites[j][
                        "href"]:
                        author.personal_website = websites[j]["href"]
            except Exception as e:
                print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            author.goodreads_link = authors_links[i]["href"]
            book.author[int] = author
        else:
            bio = ""
            photo = ""
            try:
                bio = author_soup.find("div", {"class": "aboutAuthorInfo"}).find("span",{"style": "display:none"}).get_text()
            except Exception as e:
                print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            try:
                if "nophoto" not in author_soup.find("img", {"alt": author_name})["src"]:
                    photo = base64.b64encode(
                        requests.get(author_soup.find("img", {"alt": author_name})["src"]).content).decode("utf-8")
            except Exception as e:
                print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            a = Author(photo, bio, author_name)
            try:
                websites = author_soup.find_all("a", {"itemprop": "url"})
                for j in range(0, len(websites)):
                    if "twitter" and "instagram" and "goodreads" not in websites[j]["href"] and "http" in websites[j][
                        "href"]:
                        a.personal_website = websites[j]["href"]
                    if "twitter" in websites[j]["href"] and "http" in websites[j][
                        "href"]:
                        a.twitter = websites[j]["href"]
                    if "instagram" in websites[j]["href"] and "http" in websites[j][
                        "href"]:
                        a.instagram = websites[j]["href"]
            except Exception as e:
                print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            a.goodreads_link = authors_links[i]["href"]
            book.author.append(a)
    return book


def author_google_books_scrape(book, id):
    logger.info(str(datetime.datetime.now()) + " " + "Google Books author scrape")
    brave_path = "C:\\Program Files\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    option = webdriver.ChromeOptions()
    option.binary_location = brave_path
    option.add_argument("--headless")
    browser = webdriver.Chrome(options=option)
    browser.get("https://www.google.co.za/books/edition/_/" + id + "?hl=en&gbpv=0")
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    author_names = soup.find_all(class_="U7rXJc")
    author_bios = soup.find_all(class_="qO5zb")
    authors = []

    for i in range(0, len(author_names)):
        image = ""
        author_bio = ""
        try:
            logger.info(str(datetime.datetime.now()) + " " + "Attempting to get author image")
        except Exception as e:
            print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
        try:
            logger.info("Attempting to get author bio")
            author_bio = author_bios[i].get_text()
        except Exception as e:
            print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
        authors.append(Author(image, author_bio, author_names[i].get_text()))

    book.author = authors
    return book


def google_books_api(book):
    try:
        book_details = json.loads(requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + book.isbn).text)
        try:
            book.title = book_details["items"][0]["volumeInfo"]["title"]
        except:
            pass
        try:
            book.synopsis = book_details["items"][0]["volumeInfo"]["description"]
        except:
            pass
        try:
            book.isbn = next((x["identifier"] for x in book_details["items"][0]["industryIdentifiers"] if x.type == 'ISBN_13'), book.isbn)
        except:
            pass
        try:
            book.publisher = book_details["items"][0]["volumeInfo"]["publisher"]
        except:
            pass
        try:
            for i in book_details["items"][0]["volumeInfo"]["categories"]:
                book.tags.append(i)
        except:
            pass
    except Exception as e:
        print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
        logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
    try:
        book = author_google_books_scrape(book, book_details["items"][0]["id"])
    except:
        try:
            book = author_goodreads_scrape(book)
            if (len(book.author)==0):
                for a in book_details["items"][0]["volumeInfo"]["author"]:
                    book.author.append(Author("","",a))
        except Exception as e:
            print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            try:
                if (len(book.author)==0):
                    for a in book_details["items"][0]["volumeInfo"]["author"]:
                        book.author.append(Author("","",a))
            except:
                pass
    return book


def get_books_for_the_month(month, year):
    pageNumber = 1
    html = requests.get("https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
        year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(pageNumber) + "&sort=x")
    soup = BeautifulSoup(html.content, 'html.parser')
    results = soup.find_all(attrs={'class': 'page-link'})
    pageNumber = int(results.__getitem__(len(results) - 2).get_text())

    logger.info(str(datetime.datetime.now()) + " " + month + " " + str(year) + " has " + str(
        pageNumber) + " pages of new releases")

    for i in range(1, pageNumber + 1):
        logger.info(str(datetime.datetime.now()) + " " + "Scraping year and month: " + month + " " + str(year))
        logger.info(str(datetime.datetime.now()) + " " + "Scraping page: " + str(i))

        html = requests.get("https://www.fictiondb.com/newreleases/new-books-by-month.php?date=" + month + "-" + str(
            year) + "&ltyp=3&genre=Genre&binding=a&otherfilters=n&submitted=TRUE&s=" + str(i) + "&sort=x")
        soup = BeautifulSoup(html.content, 'html.parser')
        hrefs = soup.find_all("a",class_="nowrap d-print-none")
        dates = soup.find_all("span",itemprop="datePublished")

        logger.info(str(datetime.datetime.now()) + " " + "Scraping of book table complete!")

        for i in range(0,len(hrefs)):
                book = Book()
                isbn = hrefs[i]["href"].split("&")[1].replace("isbn=","")
                book.isbn = isbn
                book.date = dates[i].get_text()
                book.goodreads_link = "https://www.goodreads.com/search?utf8=%E2%9C%93&query=" + book.isbn
                book.amazon_link = "https://www.amazon.com/s?k=" + book.isbn
                try:
                    book = google_books_api(book)
                except Exception as e:
                    print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                    logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
                book_list.append(book.__dict__)


def insert_books_into_database():
    logger.info(str(datetime.datetime.now()) + " " + "Posting to database")
    for b in book_list:
        b["_id"] = (b["isbn"] + b["title"] + b["date"]).replace(" ", "")
        authors = []
        for i in range(0, len(b.author)):
            b["author"][i]["_id"] = b["author"][i]["name"]
            authors.append(b["author"][i].__dict__)
            author_list.append(b["author"][i].__dict__)
        b["author"] = authors
    bookCollection.insert_many(book_list)
    authorCollection.insert_many(author_list)


logging.basicConfig(filename='webscraper.log', level=logging.INFO)

today = datetime.date.today()

year = today.year

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

for y in range(year - 10, year + 2):
    for m in months:
        try:
            get_books_for_the_month(m, y)
            insert_books_into_database()
            author_list.clear()
            book_list.clear()
        except Exception as e:
            print(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
            logger.error(str(datetime.datetime.now()) + " " + str(e) + "\n" + traceback.format_exc())
