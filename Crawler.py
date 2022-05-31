from bs4 import BeautifulSoup
import cloudscraper
import json
import os
import threading

ROOT_URL = "https://indiankanoon.org"
YEAR_URL = {
    "January": "/search/?formInput=doctypes:%s fromdate:1-1-%d todate: 31-1-%d",
    "February": "/search/?formInput=doctypes:%s fromdate:1-2-%d todate: 28-2-%d",
    "March": "/search/?formInput=doctypes:%s fromdate:1-3-%d todate: 31-3-%d",
    "April": "/search/?formInput=doctypes:%s fromdate:1-4-%d todate: 30-4-%d",
    "May": "/search/?formInput=doctypes:%s fromdate:1-5-%d todate: 31-5-%d",
    "June": "/search/?formInput=doctypes:%s fromdate:1-6-%d todate: 30-6-%d",
    "July": "/search/?formInput=doctypes:%s fromdate:1-7-%d todate: 31-7-%d",
    "August": "/search/?formInput=doctypes:%s fromdate:1-8-%d todate: 31-8-%d",
    "September": "/search/?formInput=doctypes:%s fromdate:1-9-%d todate: 30-9-%d",
    "October": "/search/?formInput=doctypes:%s fromdate:1-10-%d todate: 31-10-%d",
    "November": "/search/?formInput=doctypes:%s fromdate:1-11-%d todate: 30-11-%d",
    "December": "/search/?formInput=doctypes:%s fromdate:1-12-%d todate: 31-12-%d",
}


class DownloadDocument:
    def __init__(self, max_threads=10):
        self.sema = threading.Semaphore(value=max_threads)

    def T_GetDocument(self, url, dir="Dump"):

        # acquire semaphore
        self.sema.acquire()

        s = cloudscraper.create_scraper()
        temp = s.get(url, timeout=(1, 10))
        temp = BeautifulSoup(temp.text, "html5lib")
        title = temp.title.string.extract()
        title = (
            title.replace(" ", "_")
            .replace(",", "")
            .replace(".", "")
            .replace("-", "_")
            .replace("/", "_")
            + ".PDF"
        )

        if not os.path.exists(dir):
            os.makedirs(dir)

        if os.path.exists("%s/%s" % (dir, title)):
            return

        data = s.post(url, timeout=(1, 10), data={"type": "pdf"})
        assert data.status_code == 200
        pdf = data.content

        with open("%s/%s" % (dir, title), "wb") as file:
            file.write(pdf)
            file.close()

        print("[+] Downloading %s/%s" % (dir, title))
        # release semaphore
        self.sema.release()

    def GetDocument(self, url, dir="Dump"):
        """ Download Files Asynchronously """
        thread = threading.Thread(target=self.T_GetDocument, args=(url, dir))
        thread.start()


def GetPage(url):
    s = cloudscraper.create_scraper()
    print("[+] Fetching %s" % url)
    try:
        data = s.get(url, timeout=(1, 10))
        assert data.status_code == 200
    except:
        data = None
    return data


class Court:
    def __init__(self, full_name, url_name, years, links):
        self.full_name = full_name
        self.url_name = url_name
        self.years = years
        self.links = links

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)


class KanoonCrawler:
    def __init__(self):
        self.Courts = []
        pass

    def FetchCourts(self):
        BASE_URL = ROOT_URL + "/browse/"
        page = GetPage(BASE_URL)
        if page is None:
            return
        html = page.text
        soup = BeautifulSoup(html, "html5lib")

        # table0 - Courts
        # table1 - Tribunals
        # table2 - Other
        tables = soup.find_all("table")
        assert len(tables) == 3
        court_tb = tables[0]
        divs = court_tb.find_all("div")

        #  <div class="browselist">
        for div in divs:
            atags = div.a
            full_name = atags.string.extract()
            link = atags["href"]
            url_name = link[8:-1]
            yr = GetPage(ROOT_URL + link)
            if yr is None:
                continue

            yr = BeautifulSoup(yr.text, "html5lib")
            divs = yr.find_all("div", "browselist")
            links = []
            years = []
            for div in divs:
                link = ROOT_URL + div.a["href"]
                year = int(link.split("/")[-2])
                links.append(link)
                years.append(year)

            court = Court(full_name, url_name, years, links)
            self.Courts.append(court)

    def DumpCourts(self):
        with open("Courts.json", "w") as file:
            file.write(
                json.dumps(
                    self.Courts, default=lambda o: o.__dict__, sort_keys=False, indent=4
                )
            )
            file.close()

    def LoadCourts(self):
        with open("Courts.json", "r") as file:
            courts = file.read()
            file.close()
        temp = json.loads(courts)
        self.Courts = []
        for t in temp:
            full_name = t["full_name"]
            url_name = t["url_name"]
            years = t["years"]
            links = t["links"]
            court = Court(full_name, url_name, years, links)
            self.Courts.append(court)

    def FetchDocumentsByYear(self, court, year):
        documents = []
        for i, month in enumerate(YEAR_URL):
            PAGE_NO = 0
            while True:
                link = (
                    ROOT_URL
                    + YEAR_URL[month] % (court, year, year)
                    + "&pagenum=%d" % (PAGE_NO)
                )
                page = GetPage(link)
                if page is None:
                    continue
                pgsp = BeautifulSoup(page.text, "html5lib")
                atag = pgsp.find_all("a")
                curr = []
                for tag in atag:
                    if tag.string is not None:
                        if tag.string.extract() == "Full Document":
                            curr.append(ROOT_URL + tag["href"])

                if len(curr) == 0:
                    break

                documents += curr
                PAGE_NO += 1
                if PAGE_NO == 1:
                    break
        return documents

    def DownloadCourt(self, url_name):
        downloader = DownloadDocument()
        for court in self.Courts:
            if court.url_name == url_name:
                years = court.years
                for year in years:
                    documents = self.FetchDocumentsByYear(url_name, year)
                    for document in documents:
                        downloader.GetDocument(
                            document,
                            "%s/%s" % (court.full_name.replace(" ", "_"), year),
                        )
kc = KanoonCrawler()
kc.LoadCourts()
kc.DownloadCourt("kerala")
