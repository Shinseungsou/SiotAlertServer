import json
import urllib
import urllib2

from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup

import private


def parse():
    print
    url = "http://naver.com"
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
    select = soup.select("ol#realrank > li")
    result = dict()
    for rank in select:
        if len(rank.attrs) < 3:
            # print rank.attrs["value"], rank.a['title']
            result[rank.attrs["value"]] = rank.a['title']


    return result


def schdule():
    import schedule
    import time

    schedule.every().day.at('01:48').do(sendAlert)

    while True:
        schedule.run_pending()
        time.sleep(10)


def sendAlert():
    key = private.key
    get_chat = 'https://api.telegram.org/bot' + key + '/getUpdates'

    print get_chat
    chat_response = urllib2.urlopen(get_chat).read()
    chat_list = json.loads(chat_response)
    chat_id = chat_list['result'][1]['message']['chat']['id']
    rank = parse()
    text = ""
    for r in range(1, 11):
        text += str(r)+' '+rank[str(r)]+'\n'
    text = urllib.quote(text.encode('utf-8'))

    for i in chat_list['result']:
        chat_id = i['message']['chat']['id']

        url = 'https://api.telegram.org/bot' + key + '/sendMessage?chat_id=' + str(chat_id) + '&text=' + text
        print url

        message = urllib2.urlopen(url).read()
        print message
        break


def sch():
    def some_job():
        print "Decorated job"

    scheduler = BlockingScheduler()
    scheduler.add_job(some_job, 'interval', seconds=30)
    scheduler.start()

if __name__ == "__main__":
    # parser()
    # sch()
    # print parse()
    # sendAlert()
    schdule()
