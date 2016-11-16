import json
import time
import urllib
import urllib2
from datetime import datetime

from bs4 import BeautifulSoup

import private
import config

test = False

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
    select = dict()
    if(len(title) > 0):
        select['title'] = title[0].text
    contents = soup.select("li#sp_nws_all1 > dl > dd")
    print contents
    if(len(contents) > 0):
        select['contents'] = contents[1].text
    # select = soup.prettify()
    # print select.encode('utf-8')
    return select

people12 = []
minute12 = []
people6 = []
minute6 = []
isodd6 = [0, 1]

pgroup = []


def insert_news(db_connect, rank, news):
    cursor = db_connect.cursor()
    add_rank = ("insert into ranks"
                "(rank0, rank0_title, rank0_contents, rank1, rank1_title, rank1_contents, "
                "rank2, rank3, rank4, rank5, rank6, rank7, rank8, rank9, send_time)"
                "values(%(rank0)s, %(rank0_title)s, %(rank0_contents)s, %(rank1)s, %(rank1_title)s, %(rank1_contents)s, "
                "%(rank2)s, %(rank3)s, %(rank4)s, %(rank5)s, %(rank6)s, %(rank7)s, %(rank8)s, %(rank9)s, %(send_time)s)")
    news_rank = {
        'rank0': rank['1'],
        'rank0_title': news[0]['title'],
        'rank0_contents': news[0]['contents'],
        'rank1': rank['2'],
        'rank1_title': news[1]['title'],
        'rank1_contents': news[1]['contents'],
        'rank2': rank['3'],
        'rank3': rank['4'],
        'rank4': rank['5'],
        'rank5': rank['6'],
        'rank6': rank['7'],
        'rank7': rank['8'],
        'rank8': rank['9'],
        'rank9': rank['10'],
        'send_time': datetime.now()
    }
    print "------"
    print news_rank['rank0_contents']
    print "------"
    print news_rank
    print "------"
    cursor.execute(add_rank, news_rank)
    db_connect.commit()
    cursor.close()


def get_users(db_connect):
    cursor = db_connect.cursor()
    if test:
        cursor.execute("select * from user where uid = 4")
    else:
        cursor.execute("select * from user")
    users = []
    for u in cursor:
        temp_user = dict()
        temp_user['user_id'] = u[1]
        temp_user['group'] = u[2]
        users.append(temp_user)
    cursor.close()
    return users

def put_users(db_connect, users):
    cursor = db_connect.cursor()

    query = ("insert into user"
            "(chat_id) values ")
    for i in range(len(users)):
        if i < 1:
            query += '('+str(users[i])+')'
        else:
            query += ', ('+str(users[i])+')'
    print query
    cursor.execute(query)
    db_connect.commit()
    cursor.close()

def get_group(db_connect):
    cursor = db_connect.cursor()
    query = ("select * from msg_group order by uid asc")
    cursor.execute(query)
    group = []
    for g in cursor:
        temp_g = dict()
        temp_g['id'] = g[0]
        temp_g['interval'] = g[1]
        temp_g['type'] = g[2]
        group.append(temp_g)

    cursor.close()
    return group


def sendAlert(hour, minute):
    key = private.key
    get_chat = 'https://api.telegram.org/bot' + key + '/getUpdates'

    db_connect = config.mjudb().getDB()
    cursor = db_connect.cursor()

    print get_chat
    chat_response = urllib2.urlopen(get_chat).read()
    chat_list = json.loads(chat_response)
    # chat_id = chat_list['result'][1]['message']['chat']['id']
    rank, news = parse()
    insert_news(db_connect, rank, news)
    print "rank"
    print rank
    print news
    print 'news'
    for i in news:
        print i
    text = ""
    for r in range(1, 11):
        text += str(r)+' '+rank[str(r)]
        if r <= 2:
            text += news[r-1]['title'] + " - " + news[r-1]['contents'] + '\n'
        else:
            text += '\n'
    raw_text = text
    text = urllib.quote(text.encode('utf-8'))
    print
    print raw_text
    print

    users = get_users(db_connect)
    new_users = []

    for i in chat_list['result']:
        if not contains_user(i['message']['chat']['id'], users):
            new_users.append(i['message']['chat']['id'])
    print new_users
    if not test:
        put_users(db_connect, new_users)
    if(False):
        print users, users[0]
        db_connect.close()
        cursor.close()
        return

    # for i in users:
    # for i in chat_list['result']:
    # for i in chat_list['result']:
    for i in users:
        # chat_id = i['message']['chat']['id']
        # chat_id = 202959968
        chat_id = i['user_id']
        group_id = i['group']
        now = datetime.now()
        group_interval = pgroup[int(group_id) - 1]['interval']
        print group_id, i, ' | ', now.minute % 2
        if group_id and (compare_time(group_interval)) and now.minute % 2 == group_interval - 1:
            send_msg(chat_id, text)


    db_connect.close()
    cursor.close()

def contains_user(user, users):
    for u in users:
        print user, ' with ', u['user_id']
        if user == u['user_id']:
            return True
    return False

def compare_time(interval):
    min = interval % 1
    hour = interval / 1
    rate = datetime.now().hour - startHour
    if rate % hour == 0 and (min == 0 or rate % interval == 0):
        return True
    return False

start_date = datetime(2016, 11, 11, 02, 0)
end_date = datetime(2016, 11, 22, 22, 24)

def send_msg(chat_id, text):
    key = private.key
    url = 'https://api.telegram.org/bot' + key + '/sendMessage?chat_id=' + str(chat_id) + '&text=' + text
    print url
    # print "12 : ", chat_id in people12, "; 6 : ", chat_id in people6
    try:
        message = urllib2.urlopen(url).read()
        print message
    except urllib2.HTTPError:
        print "fail"


startHour = 10
endHour = 19
startDay = 9
endDay = 15

# TIMEZONE
startHour -= 9
endHour -= 9
sleep_sec = 60
def timer():

    while True:
        now = datetime.now()
        if now > end_date and now < start_date:
            print start_date, ' : ', now, ':', end_date, "bye", now - end_date
            break
        if endHour <= now.hour < startHour and (now.minute in [30, 0]):
            print "send alert ", now
            sendAlert(now.hour, now.minute)
        else:
            print "deep sleep ", now
        delay = 30 - now.minute % 30
        time.sleep(sleep_sec * delay)

        # if startHour <= now.hour <= endHour and (now.minute in [40, 41, 47, 48, 52, 54]): #For desktop
        # if startHour <= now.hour <= endHour and (now.minute in [30, 0, 39, 40, 41, 42, 43, 44, 45]): #For server
        #if startHour <= now.hour <= endHour and (now.minute in [30, 0]):#,10,20,40,50]): #For server
        # if startHour <= now.hour <= endHour ): #For server
        #     pass
        # else:
        #     print "sleep ", now
        #     time.sleep(sleep_sec)

if __name__ == "__main__":
    db_connect = config.mjudb().getDB()
    pgroup = get_group(db_connect)
    db_connect.close()

    timer()

    # sendAlert(1,1)
    # hh = [3, 7, 31, 59, 60, 30, 0] #27, 23, 29, 1, 0, 0, 0
    # div = 30
    # defa = 30
    # for i in hh:
    #     print defa - i % div,
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
