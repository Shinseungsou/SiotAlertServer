from bs4 import BeautifulSoup
import urllib2
from apscheduler.schedulers.blocking import BlockingScheduler


def parse():
    print
    url = "http://naver.com"
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
    select = soup.select("ol#realrank > li")
    for rank in select:
        if len(rank.attrs) < 3:
            print rank.attrs["value"], rank.a['title']

def schdule():
    import schedule
    import time

    def job(t):
        print "I'm working...", t
        return

    schedule.every().day.at("02:57").do(job,'It is 01:00')

    while True:
        schedule.run_pending()
        time.sleep(10)

def sch():
    def some_job():
        print "Decorated job"

    scheduler = BlockingScheduler()
    scheduler.add_job(some_job, 'interval', seconds=30)
    scheduler.start()

if __name__ == "__main__":
    # parser()
    sch()
