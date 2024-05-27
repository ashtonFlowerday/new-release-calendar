import base64
import json
import re

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

    def __init__(self,p,b,n):
        self.photo = p
        self.bio = b
        self.name = n

def author_goodreads_scrape(book):
    logger.info("Goodreads author scrape")
    html = requests.get("https://www.goodreads.com/search?q="+book.isbn)
    soup = BeautifulSoup(html.content, 'html.parser')
    authors_links = soup.find(class_="ContributorLinksList").find_all("a")
    try:
        authors = []
        for i in range(0, len(authors_links)):
            author_html = requests.get(i["href"])
            author_soup = BeautifulSoup(author_html.content, 'html.parser')
            image = base64.b64encode(requests.get(author_soup.find(class_="authorPhoto")["src"]).content).decode("utf-8")
            authors.append(Author(image, author_soup.find(class_="fullContent"),author_soup.find("authorName").get_text()))
        book.author = authors
    except Exception as e:
        logger.error(e)
        return author_amazon_scrape(book)
    return book

def author_amazon_scrape(book):
    logger.info("Amazon author scrape")
    html = requests.get("https://www.amazon.com/s?k="+book.isbn)
    soup = BeautifulSoup(html.content, 'html.parser')
    try:
        book_html=requests.get(soup.find(class_="a-link-normal s-faceout-link a-text-normal")["href"])
        book_soup = BeautifulSoup(book_html.content, 'html.parser')
        author_links = book_soup.find_all(class_="bylineContributor")
        authors = []
        for i in author_links:
            author_html=requests.get(i["href"])
            author_soup = BeautifulSoup(author_html.content, 'html.parser')
            author_html = requests.get(author_soup.select_one('[data-testid="product-brand"]')["href"])
            author_soup = BeautifulSoup(author_html.content, 'html.parser')
            image = base64.b64encode(requests.get(author_soup.find(class_="AuthorBio__author-bio__author-picture__hz4cs").find("img")["href"]).content).decode("utf-8")
            authors.append(Author(image, author_soup.find(class_="AuthorBio__author-bio__author-biography__WeqwH").get_text(),author_soup.find(class_="AuthorSubHeader__author-subheader__name__HkJyX").get_text()))

        book.author = authors
    except Exception as e:
        logger.error(e)
    return book

def author_google_books_scrape(book, id):
    logger.info("Google Books author scrape")
    title = re.sub(r'\W+', '',book.title).replace(" ","_")
    html = requests.get("https://www.google.co.za/books/edition/"+title+"/"+id+"?hl=en")
    soup = BeautifulSoup(html.content, 'html.parser')
    try:
        author_names = soup.find_all(class_ = "U7rXJc")
        author_bios = soup.find_all(class_ = "qO5zb")
        author_photos = soup.find_all(class_="IXgIFd")
        authors = []

        for i in range(0,len(author_names)):
            image = base64.b64encode(requests.get(author_photos[i].find("a")["href"]).content).decode("utf-8")
            authors.append(Author(image,author_bios[i].get_text(),author_names[i].get_text()))

        book.author = authors

    except Exception as e:
        logger.error(e)
        return author_goodreads_scrape(book)
    return book

def google_books_api(book):
    book_details = json.loads(requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+book.isbn).text)
    book.date = book_details["items"][0]["volumeInfo"]["publishedDate"]
    book.publisher = book_details["items"][0]["volumeInfo"]["publisher"]
    for i in book_details["items"][0]["volumeInfo"]["categories"]:
        book.tags.append(i)
    author_google_books_scrape(book,book_details["items"][0]["id"])
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