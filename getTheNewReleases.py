import concurrent.futures
import requests
from bs4 import BeautifulSoup
import datetime

today = datetime.date.today()

year = today.year

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

newReleases = []


class Book():
    author = ""
    title = ""
    date = ""
    genre = ""

    def construct(self, a, t, d, g):
        author = a
        title = t
        date = d
        genre = g
        return self


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
                book = Book().construct(b.find(attrs={'itemprop': 'author'}).get_text(),
                                        b.find(attrs={'itemprop': 'name'}).get_text(),
                                        b.find(attrs={'itemprop': 'datePublished'}).get_text(),
                                        b.find(attrs={'itemprop': 'genre'}).get_text())
                print(book.__dict__)
                newReleases.append(book)
            except:
                print("oops")


for m in months:
    getBooksForTheMonth(m)
