import json
import time
import urllib
import urllib2
from datetime import datetime
from config import config
from bs4 import BeautifulSoup

import private


def parse():
    print
    url = "http://naver.com"
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
    select = soup.select("ol#realrank > li")
    result = dict()
    news = []
    for rank in select:
        if len(rank.attrs) < 3:
            print rank.attrs["value"].encode('utf-8'),
            print rank.a['title'].encode('utf-8')
            result[rank.attrs["value"]] = rank.a['title']
            if(int(rank.attrs["value"]) <= 2):
                result[rank.attrs["value"]] += "\n"
                news.append(parseNews(rank.a.attrs["href"]))

    return result, news

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

    db = config.mjudb().getDB()
    cursor = db.cursor()


    print get_chat
    chat_response = urllib2.urlopen(get_chat).read()
    chat_list = json.loads(chat_response)
    # chat_id = chat_list['result'][1]['message']['chat']['id']
    rank, news = parse()
    for r in rank:
        cursor.execute("", )
    print rank
    text = ""
    for r in range(1, 11):
        text += str(r)+' '+rank[str(r)]+'\n'
    text = urllib.quote(text.encode('utf-8'))

    cursor.execute("select * from user")
    print tuple([d[0] for d in cursor.description])
    users = []
    for u in cursor:
        users.append(u[1])
    db.close()

    for i in users:
        # chat_id = i['message']['chat']['id']
        # chat_id = 202959968
        chat_id = i

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


start_date = datetime(2016, 11, 11, 02, 0)
end_date = datetime(2016, 11, 22, 22, 24)

def timer():
    startHour = 9
    endHour = 19
    startDay = 9
    endDay = 15

    # TIMEZONE
    startHour -= 9
    endHour -= 9
    sleep_sec = 60

    while True:
        now = datetime.now()
        if now > end_date and now < start_date:
            print start_date, ' : ', now, ':', end_date, "bye", now - end_date
            break
        if (now.hour >= endHour or now.hour < startHour):
            print "deep sleep"
            time.sleep(sleep_sec * 30)
        print "current time", now

        # if startHour <= now.hour <= endHour and (now.minute in [40, 41, 47, 48, 52, 54]): #For desktop
        # if startHour <= now.hour <= endHour and (now.minute in [30, 0, 39, 40, 41, 42, 43, 44, 45]): #For server
        #if startHour <= now.hour <= endHour and (now.minute in [30, 0]):#,10,20,40,50]): #For server
        if startHour <= now.hour <= endHour and (now.minute in [30, 0]): #For server
            print "send alert ", now
            sendAlert(now.hour, now.minute)
            time.sleep(sleep_sec)
        else:
            print "sleep ", now
            time.sleep(sleep_sec)

if __name__ == "__main__":
    timer()
    # print end_date - start_date, datetime.now()-start_date, (start_date - datetime.now()).total_seconds() < 0




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
