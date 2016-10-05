import json
import time
import urllib
import urllib2
from datetime import datetime

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
            print rank.attrs["value"].encode('utf-8'),
            print rank.a['title'].encode('utf-8')
            result[rank.attrs["value"]] = rank.a['title']
            if(int(rank.attrs["value"]) <= 2):
                result[rank.attrs["value"]] += "\n"
                result[rank.attrs["value"]] += parseNews(rank.a.attrs["href"])

    return result

def parseNews(url):
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
    title = soup.select("li#sp_nws_all1 > dl > dt")
    print title
    select = ""
    if(len(title) > 0):
        select += title[0].text
        select += " - "
    contents = soup.select("li#sp_nws_all1 > dl > dd")
    print contents
    if(len(contents) > 0):
        select += contents[1].text
    # select = soup.prettify()
    print select.encode('utf-8')
    return select

people12 = []
minute12 = []
people6 = []
minute6 = []
isodd6 = [0, 1]

def sendAlert(hour, minute):
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
        if (chat_id not in people12 and chat_id not in people6) \
                or (chat_id in people12 and minute in minute12) \
                or (chat_id in people6 and minute in minute6 and hour % 2 in isodd6):
            url = 'https://api.telegram.org/bot' + key + '/sendMessage?chat_id=' + str(chat_id) + '&text=' + text
            print url
            # print "12 : ", chat_id in people12, "; 6 : ", chat_id in people6
            try:
                message = urllib2.urlopen(url).read()
                print message
            except urllib2.HTTPError:
                print "fail"


end_date = datetime(2016, 9, 22, 22, 24)
start_date = datetime(2016, 9, 22, 10, 0)

def timer():
    startHour = 10
    endHour = 21
    startDay = 9
    endDay = 10

    # TIMEZONE
    startHour -= 9
    endHour -= 9
    sleep_sec = 60

    while True:
        now = datetime.now()
        if now > end_date:
            print now, ':', end_date, "bye", now - end_date
            break
        if (now.hour >= endHour or now.hour < startHour):
            print "deep sleep"
            time.sleep(sleep_sec * 30)
        print "current time", now

        # if startHour <= now.hour <= endHour and (now.minute in [40, 41, 47, 48, 52, 54]): #For desktop
        if startHour <= now.hour <= endHour and (now.minute in [30, 0]): #For server
            print "send alert ", now
            sendAlert(now.hour, now.minute)
            time.sleep(sleep_sec)
        else:
            print "sleep ", now
            time.sleep(sleep_sec)

if __name__ == "__main__":
    timer()




#
# def scheduler1(hour, mins, count, MAX):
#     print "schedule1"
#     if count >= MAX:
#         return
#     else:
#         count += 1
#
#     mins += 1
#     if mins >= 60:
#         hour += 1
#         mins = 0
#     if hour == 24:
#         hour = 0
#     print "time : ", hour, ':', mins
#     print "count : ", count, '/', MAX
#     pass_count = count
#     schedule.every().days.at(str(hour)+':'+str(mins)).do(job, hour, mins, pass_count, MAX)
#     while True:
#         schedule.run_pending()
#         time.sleep(10)
#
#
# def scheduler30(hour, mins, count, MAX):
#     if count >= MAX:
#         return
#     else:
#         count += 1
#
#     if mins == 30:
#         hour += 1
#         mins = 0
#     else:
#         mins = 30
#
#     if hour == 24:
#         hour = 0
#     schedule.every(60).days.at(str(hour)+':'+str(mins)).do(job, hour, mins, count, MAX)
#     while True:
#         schedule.run_pending()
#         time.sleep(10)
#
# def job(hour, mins, count, MAX):
#     print "send!"
#     print "time : ", hour, ':', mins
#     print "count : ", count, '/', MAX
#     sendAlert()
#     scheduler1(hour, mins, count, MAX)
#
#
#
# def sch():
#     def some_job():
#         print "Decorated job"
#
#     scheduler = BlockingScheduler()
#     scheduler.add_job(some_job, 'interval', seconds=30)
#     scheduler.start()
