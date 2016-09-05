import json
import urllib
import urllib2

from apscheduler.schedulers.blocking import BlockingScheduler

from bs4 import BeautifulSoup

import private
import schedule
import time


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
    #
    # schedule.every().day.at('14:25').do(sendAlert)
    # schedule.every().day.at('14:27').do(sendAlert)
    # schedule.every().day.at('14:29').do(sendAlert)
    # schedule.every().day.at('14:31').do(sendAlert)
    # schedule.every().day.at('14:33').do(sendAlert)
    # schedule.every().day.at('14:35').do(sendAlert)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)
    scheduler1(00, 28, 0, 3)


def scheduler1(hour, mins, count, MAX):
    print "schedule1"
    if count >= MAX:
        return
    else:
        count += 1

    mins += 1
    if mins >= 60:
        hour += 1
        mins = 0
    if hour == 24:
        hour = 0
    print "time : ", hour, ':', mins
    print "count : ", count, '/', MAX
    pass_count = count
    schedule.every().days.at(str(hour)+':'+str(mins)).do(job, hour, mins, pass_count, MAX)
    while True:
        schedule.run_pending()
        time.sleep(10)


def scheduler30(hour, mins, count, MAX):
    if count >= MAX:
        return
    else:
        count += 1

    if mins == 30:
        hour += 1
        mins = 0
    else:
        mins = 30

    if hour == 24:
        hour = 0
    schedule.every(60).days.at(str(hour)+':'+str(mins)).do(job, hour, mins, count, MAX)
    while True:
        schedule.run_pending()
        time.sleep(10)

def job(hour, mins, count, MAX):
    print "send!"
    print "time : ", hour, ':', mins
    print "count : ", count, '/', MAX
    sendAlert()
    scheduler1(hour, mins, count, MAX)

def sendAlert():
    key = private.key
    get_chat = 'https://api.telegram.org/bot' + key + '/getUpdates'

    print get_chat
    chat_response = urllib2.urlopen(get_chat).read()
    chat_list = json.loads(chat_response)
    # chat_id = chat_list['result'][1]['message']['chat']['id']
    rank = parse()
    text = ""
    for r in range(1, 11):
        text += str(r)+' '+rank[str(r)]+'\n'
    text = urllib.quote(text.encode('utf-8'))

    for i in chat_list['result']:
        chat_id = i['message']['chat']['id']

        url = 'https://api.telegram.org/bot' + key + '/sendMessage?chat_id=' + str(chat_id) + '&text=' + text
        print url
        try:
            message = urllib2.urlopen(url).read()
            print message
        except urllib2.HTTPError:
            print "fail"


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
