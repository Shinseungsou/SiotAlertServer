# -*- coding: utf-8 -*-
import json
import time
import urllib
import urllib2
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

import private
import config

test = True
print_news = True
print_db = True
print_alert = True


start_date = datetime(2016, 11, 11, 02, 0)
end_date = datetime(2016, 11, 30, 22, 24)

startHour = 10
endHour = 23

# TIMEZONE
startHour -= 9
endHour -= 9
sleep_sec = 60

def parse():
    if print_news:
        print
    url = "http://naver.com"
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
    select = soup.select("ol#realrank > li")
    result = dict()
    news = []
    twit = []
    for rank in select:
        if len(rank.attrs) < 3:
            if print_news:
                print rank.attrs["value"].encode('utf-8'),
                print rank.a['title'].encode('utf-8'),
            rk = rank.select("span.rk")
            tx = rank.select("span.tx")
            up = ""
            if len(rk) == 0:
                up = tx[0].text
            else:
                up = tx[0].text + " " + rk[0].text
            if print_news:
                print up.encode('utf-8')
            result["up"+rank.attrs["value"]] = up
            result[rank.attrs["value"]] = rank.a['title']
            if(int(rank.attrs["value"]) <= 2):
                news.append(parseNews(rank.a.attrs["href"]))
                twit.append(parseTweet(rank.a['title']))

    return result, news, twit

def parseNews(url):
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
    title = soup.select("li#sp_nws_all1 > dl > dt")
    if print_news:
        print title
    select = dict()
    if(len(title) > 0):
        select['title'] = title[0].text
    contents = soup.select("li#sp_nws_all1 > dl > dd")
    if print_news:
        print contents
    if(len(contents) > 0):
        select['contents'] = contents[1].text
    # select = soup.prettify()
    # print select.encode('utf-8')
    return select

'''
 [timestamp] text - retweet or like
'''
def parseTweet(keyword):
    result = []
    keyword = urllib.quote(keyword.encode('utf-8'))
    for best in range(0, 2):
        url = "https://search.naver.com/search.naver?where=realtime&ie=utf8&sm=tab_srt&section=0&best="+str(best)+"&mson=0&query=" + keyword
        print url, best
        r = urllib2.urlopen(url)
        soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
        i = 0
        for l in soup.select("div.rt_wrap > div > ul > li > dl"):
            twit = dict()
            print l.select("span.user_name")[0].text.encode('utf-8'), " - ",
            twit['name'] = l.select("span.user_name")[0].text
            print l.select("dd:nth-of-type(2)")[0].text.encode('utf-8')
            twit['text'] = l.select("dd:nth-of-type(2)")[0].text
            print l.select("._timeinfo")[0].text.encode('utf-8'), " | ",
            twit['time'] = l.select("._timeinfo")[0].text
            if len(l.select(".sub_reply")) > 0:
                print l.select(".sub_reply")[0].text.encode('utf-8')," | ",
            if len(l.select(".sub_like")) > 0:
                print l.select(".sub_like")[0].text.encode('utf-8')," | ",
                twit['retweet'] = l.select(".sub_like")[0].text
                print l.select(".sub_dis")[0].text.encode('utf-8')
            elif len(l.select(".sub_retweet")) > 0:
                print l.select(".sub_retweet")[0].text.encode('utf-8')," | ",
                print l.select(".sub_interest")[0].text.encode('utf-8')
                twit['retweet'] = l.select(".sub_retweet")[0].text
            if not twit.has_key('retweet'):
                twit['retweet'] = ""
            result.append(twit)
            if i >= 1:
                break
            i += 1
    while len(result) < 4:
        print "len " + str(len(result))
        twit = dict()
        twit['name'] = ""
        twit['text'] = ""
        twit['time'] = ""
        twit['retweet'] = ""
        result.append(twit)
    print result
    return result


people12 = []
minute12 = []
people6 = []
minute6 = []
isodd6 = [0, 1]

pgroup = []


def insert_news(db_connect, rank, news, twit):
    cursor = db_connect.cursor()
    add_rank = ("insert into ranks"
                "(rank0, up0, rank0_title, rank0_contents, rank1, up1, rank1_title, rank1_contents, "
                "rank2, up2, rank3, up3, rank4, up4, rank5, up5, "
                "rank6, up6, rank7, up7, rank8, up8, rank9, up9, send_time)"
                "values(%(rank0)s, %(up0)s, %(rank0_title)s, %(rank0_contents)s, "
                "%(rank1)s, %(up1)s, %(rank1_title)s, %(rank1_contents)s, "
                "%(rank2)s, %(up2)s, %(rank3)s, %(up3)s, %(rank4)s,%(up4)s,  %(rank5)s, %(up5)s, "
                "%(rank6)s, %(up6)s, %(rank7)s, %(up7)s, %(rank8)s, %(up8)s, %(rank9)s, %(up9)s, %(send_time)s)")
    news_rank = {
        'rank0': rank['1'],
        'rank0_title': news[0]['title'],
        'rank0_contents': news[0]['contents'],
        'up0': rank['up1'],
        'rank1': rank['2'],
        'rank1_title': news[1]['title'],
        'rank1_contents': news[1]['contents'],
        'up1': rank['up2'],
        'rank2': rank['3'],
        'up2': rank['up3'],
        'rank3': rank['4'],
        'up3': rank['up4'],
        'rank4': rank['5'],
        'up4': rank['up5'],
        'rank5': rank['6'],
        'up5': rank['up6'],
        'rank6': rank['7'],
        'up6': rank['up7'],
        'rank7': rank['8'],
        'up7': rank['up8'],
        'rank8': rank['9'],
        'up8': rank['up9'],
        'rank9': rank['10'],
        'up9': rank['up10'],
        'send_time': datetime.now()
    }
    if print_db:
        print "------"
        print news_rank['rank0_contents'].encode('utf-8')
        print "------"
        print news_rank
        print "------"
    cursor.execute(add_rank, news_rank)
    lastrow_id = cursor.lastrowid
    insert_twit = ('insert into twit (rank_id, rank, '
                   'twit1_0_text, twit1_0_retweet, twit1_0_time, twit1_1_text, twit1_1_retweet, twit1_1_time, '
                   'twit2_0_text, twit2_0_retweet, twit2_0_time, twit2_1_text, twit2_1_retweet, twit2_1_time) '
                   'value (%s, %s, '
                   '%s, %s, %s, %s, %s, %s, '
                   '%s, %s, %s, %s, %s, %s)')
    print twit[0][0]
    new_twit = (
        lastrow_id,
        0,
        twit[0][0]['text'],
        twit[0][0]['retweet'],
        twit[0][0]['time'],
        twit[0][1]['text'],
        twit[0][1]['retweet'],
        twit[0][1]['time'],
        twit[0][2]['text'],
        twit[0][2]['retweet'],
        twit[0][2]['time'],
        twit[0][3]['text'],
        twit[0][3]['retweet'],
        twit[0][3]['time']
    )
    cursor.execute(insert_twit, new_twit)
    new_twit = (
        lastrow_id,
        1,
        twit[1][0]['text'],
        twit[1][0]['retweet'],
        twit[1][0]['time'],
        twit[1][1]['text'],
        twit[1][1]['retweet'],
        twit[1][1]['time'],
        twit[1][2]['text'],
        twit[1][2]['retweet'],
        twit[1][2]['time'],
        twit[1][3]['text'],
        twit[1][3]['retweet'],
        twit[1][3]['time']
    )
    cursor.execute(insert_twit, new_twit)
    twit_id = cursor.lastrowid

    db_connect.commit()
    cursor.close()
    return lastrow_id


def get_users(db_connect):
    cursor = db_connect.cursor()
    if test:
        cursor.execute("select * from user where uid = 4 or chat_id = 202959968")# or chat_id = 247427433")
    else:
        cursor.execute("select * from user")
    users = []
    for u in cursor:
        temp_user = dict()
        temp_user['user_id'] = u[1]
        temp_user['group_id'] = u[2]
        users.append(temp_user)
    cursor.close()
    return users


def put_users(db_connect, users):
    cursor = db_connect.cursor()

    query = ("insert into user"
            "(chat_id, group_id) values ")
    for i in range(len(users)):
        if i < 1:
            query += '('+str(users[i])+', 1)'
        else:
            query += ', ('+str(users[i])+', 1)'
    if print_db:
        print query
    cursor.execute(query)
    db_connect.commit()
    cursor.close()


def put_messages(db_connect, messages):
    cursor = db_connect.cursor()

    query = ("insert into chat"
            "(chat_id, update_id, text, date) values (%s, %s, %s, %s)")
    val = []
    for i in messages.keys():
        for m in messages[i]:
            v = (
                i, m['update_id'], m['text'], m['date']
            )
            val.append(v)
    if print_db:
        print query
    for i in val:
        print i
    cursor.executemany(query, val)
    db_connect.commit()
    cursor.close()

def get_latest_chat(db_connect):
    cursor = db_connect.cursor()
    query = "select * from chat order by date desc limit 1"
    cursor.execute(query)
    for c in cursor:
        return c[2]

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


def get_notice(type):
    tt = 6
    if tt == 0:
        if type == 1:
            text = (u"오늘은 어제와 다른 구성의 알림이 발송됩니다. \n\n참가자님께서는 2시간마다 *'네이버 실시간 검색어 1-10순위'*와 *'상승량'*을 알림으로 받아보시게 됩니다. \n\n매일 저녁, 수신하신 검색어 정보 수용도를 *설문으로* 확인할 예정입니다. \n\n그럼, 알림 봇과 즐거운 시간 보내세요! :-)\n\n(푸쉬 알림은 5일간 오전 10시부터 오후 8시까지 2시간 간격으로 일 6회 발송됩니다.)")
        elif type == 2:
            text = (u"오늘은 어제와 다른 구성의 알림이 발송됩니다. \n\n참가자님께서는 2시간마다 *'네이버 실시간 검색어 1-10순위'*+ *'1,2위 검색어에 대한 트윗/소셜 반응'*을 알림으로 받아보시게 됩니다.\n\n정제하지 않은 트윗/소셜 멘션 그대로이기에, 다소 험한 말(욕설)을 포함한 반응들이 있더라도 너그러이 생각해주세요 :\*\n\n매일 저녁, 수신하신 검색어와 소셜정보 수용도를 *설문으로* 확인할 예정입니다. \n\n그럼, 알림 봇과 즐거운 시간 보내세요! :-)\n\n(푸쉬 알림은 5일간 오전 10시부터 오후 8시까지 2시간 간격으로 일 6회 발송됩니다.)")
        elif type == 3:
            text = (u"오늘은 어제와 다른 구성의 알림이 발송됩니다. \n\n참가자님께서는 2시간마다 *'네이버 실시간 검색어 1-10순위'*+ *'1,2위 검색어에 대한 뉴스 기사 요약'*을 알림으로 받아보시게 됩니다.\n\n매일 저녁, 수신하신 검색어와 뉴스 기사정보 수용도를 *설문으로* 확인할 예정입니다. \n\n그럼, 알림 봇과 즐거운 시간 보내세요! :-)\n\n(푸쉬 알림은 5일간 오전 10시부터 오후 8시까지 2시간 간격으로 일 6회 발송됩니다.)")
    elif tt == 1:
        if type == 1:
            text = (u"\n<1일차 알림 봇, 자러가기 전 부탁드립니다>\n\n1일차 실험이 종료되었습니다. 감사합니다.\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/sQRMAiZ3Oadb6MaA2\n(내일부터는 설문 문항이 더욱 짧아질 예정입니다.)\n\n감사합니다. 좋은 밤 보내세요!")
        elif type == 2:
            text = (u"\n<1일차 알림 봇, 자러가기 전 부탁드립니다>\n\n1일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/jZWnrM8H37hfRu9A3\n(내일부터는 설문 문항이 더욱 짧아질 예정입니다.)\n\n감사합니다. 좋은 밤 보내세요!")
        elif type == 3:
            text = (u"\n<1일차 알림 봇, 자러가기 전 부탁드립니다>\n\n1일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/0JEQ43YZO6NyK6H02\n(내일부터는 설문 문항이 더욱 짧아질 예정입니다.)\n\n감사합니다. 좋은 밤 보내세요!")
    elif tt == 2:
        if type == 1:
            text = (u"\n<설문지 오류로, 새로운 링크로 응답을 부탁드립니다>\n\n너무나도 죄송합니다... ㅠㅠㅠ\n서버 오류로 설문지 형식이 잘못 발송되었습니다.\n\n아직 설문을 하지 않으신 분께서는, 아래 링크로 설문을 완료해주세요.\nhttps://goo.gl/forms/IEtHQSSCmrWthZqF2\n\n혼란을 드려 죄송합니다. 감사합니다!")
        elif type == 2:
            text = (u"\n<설문지 오류로, 새로운 링크로 응답을 부탁드립니다>\n\n너무나도 죄송합니다... ㅠㅠㅠ\n서버 오류로 설문지 형식이 잘못 발송되었습니다.\n\n아직 설문을 하지 않으신 분께서는, 아래 링크로 설문을 완료해주세요.\nhttps://goo.gl/forms/f5f428qbFT243h112\n\n혼란을 드려 죄송합니다. 감사합니다!")
        elif type == 3:
            text = (u"\n<설문지 오류로, 새로운 링크로 응답을 부탁드립니다>\n\n너무나도 죄송합니다... ㅠㅠㅠ\n서버 오류로 설문지 형식이 잘못 발송되었습니다.\n\n아직 설문을 하지 않으신 분께서는, 아래 링크로 설문을 완료해주세요.\nhttps://goo.gl/forms/VUJ2WSABHuT2stA53\n\n혼란을 드려 죄송합니다. 감사합니다!")
    elif tt == 3:
        if type == 1:
            text = (u"<3일차 알림 봇, 첫눈과 함께 찾아왔습니다>\n\n3일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/sPtKl1sLirfM1YKB2\n\n감사합니다. 추운날씨에 감기 조심하세요!")
        elif type == 2:
            text = (u"<3일차 알림 봇, 첫눈과 함께 찾아왔습니다>\n\n3일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/AMAIkiRj3U88NlMt1\n\n감사합니다. 추운날씨에 감기 조심하세요!")
        elif type == 3:
            text = (u"<3일차 알림 봇, 첫눈과 함께 찾아왔습니다>\n\n3일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/IiAb93smpwoJA2bS2\n\n감사합니다. 추운날씨에 감기 조심하세요!")
    elif tt == 4:
        if type == 1:
            text = (u"<4일차 알림 봇, 설문을 부탁드립니다>\n\n4일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/perRXVWmYTHdtojX2\n\n감사합니다. 좋은 저녁 보내세요!")
        elif type == 2:
            text = (u"<4일차 알림 봇, 설문을 부탁드립니다>\n\n4일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/GcWazizqB2r4jX673\n\n감사합니다. 좋은 저녁 보내세요!")
        elif type == 3:
            text = (u"<4일차 알림 봇, 설문을 부탁드립니다>\n\n4일차 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/RlDl21rwoBewEbXI3\n\n감사합니다. 좋은 저녁 보내세요!")
    elif tt == 5:
        text = (u"실험 마지막 날입니다! 오늘은 어제 선택하신 형식으로 알림이 발송됩니다.\n\n오늘 저녁 9시 경, 검색어와 정보 수용도를 마지막으로 확인한 이후 실험이 종료됩니다.\n함께해주셔서 감사합니다. 마지막 하루까지, 알림 봇과 즐거운 시간 보내세요! :-)\n\n(푸쉬 알림은 오전 10시부터 오후 8시까지 2시간 간격으로 일 6회 발송됩니다.)")
    elif tt == 6:
        if type == 1:
            text = (u"<5일차 알림 봇, 마지막 설문 부탁드립니다>\n\n5일차로 모든 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/To9Ke6pZ4QPqwHM23\n\n그동안 감사했습니다. 좋은 일만 가득하세요!")
        elif type == 2:
            text = (u"<5일차 알림 봇, 마지막 설문 부탁드립니다>\n\n5일차로 모든 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/X86WiaJznTapAj9f2\n\n그동안 감사했습니다. 좋은 일만 가득하세요!")
        elif type == 3:
            text = (u"<5일차 알림 봇, 마지막 설문 부탁드립니다>\n\n5일차로 모든 실험이 종료되었습니다. 감사합니다!\n아래 링크에서 설문을 부탁드립니다.\nhttps://goo.gl/forms/vMyGwmNowC1hOnsH2\n\n그동안 감사했습니다. 좋은 일만 가득하세요!")


    return text


def get_text(rank, news, twit, type):
    text = ""
    if type == 1:
        for r in range(1, 11):
            text += str(r)+'.'
            text += ' *' + rank[str(r)] + '*'
            text += ' \['+rank['up'+str(r)] + '] '
            text += '\n'
    elif type == 2:
        for r in range(1, 11):
            text += str(r)+'.'
            text += ' *' + rank[str(r)] + '*'
            text += ' \[' + rank['up'+str(r)] + '] '
            text += '\n'
            if r <= 2:
                for t_row in range(0, 4):
                    print twit[r-1][t_row]

                    if len(twit[r-1][t_row]['time']) > 0:
                        if t_row > 0:
                            text += '|\n'
                        text += '- ' + twit[r-1][t_row]['text'] + ' - *' + twit[r-1][t_row]['retweet'] + '*'
                        text += '\n'
                text += '\n'
    elif type == 3:
        for r in range(1, 11):
            text += str(r)+'. '
            text += '*' + rank[str(r)] + '*'
            text += ' \['+rank['up'+str(r)] + '] '
            text += '\n'
            if r <= 2:
                text += '- \[' + news[r-1]['title'] + "] - " + news[r-1]['contents'] + '\n\n'
    return text

mock_response = ('{"ok":true,"result":['
                 '{"update_id":343241004,"message":{"message_id":1763,"from":{"id":191911803,"first_name":"\ud604\uc815","last_name":"\uc774"},"chat":{"id":191911803,"first_name":"\ud604\uc815","last_name":"\uc774","type":"private"},"date":1480659186,"text":"Gaebalja"}},'
                '{"update_id":343241005,"message":{"message_id":1764,"from":{"id":202959968,"first_name":"\uc2b9\uc218"},"chat":{"id":202959968,"first_name":"\uc2b9\uc218","type":"private"},"date":1480738155,"text":"\uc548\ub155?"}},'
                '{"update_id":343241006,"message":{"message_id":1765,"from":{"id":202959968,"first_name":"\uc2b9\uc218"},"chat":{"id":202959968,"first_name":"\uc2b9\uc218","type":"private"},"date":1480738157,"text":"\ub09c"}},'
                '{"update_id":343241007,"message":{"message_id":1766,"from":{"id":202959968,"first_name":"\uc2b9\uc218"},"chat":{"id":202959968,"first_name":"\uc2b9\uc218","type":"private"},"date":1480738171,"text":"\uc2a4\uc2a4\uc2a4"}},'
                '{"update_id":343241008,"message":{"message_id":1767,"from":{"id":202959968,"first_name":"\uc2b9\uc218"},"chat":{"id":202959968,"first_name":"\uc2b9\uc218","type":"private"},"date":1480738172,"text":"\uc57c"}}]}')

def parse_message(chat_list, last_chat_id):
    message = dict()
    for i in chat_list:
        user_id = i['message']['chat']['id']
        chat = dict()
        chat['update_id'] = i['update_id']
        chat['date'] = datetime.utcfromtimestamp(i['message']['date'])
        chat['text'] = i['message']['text']
        if print_alert :

            print i['update_id'],
            print i['message']['date'], datetime.utcfromtimestamp(i['message']['date']),
            print i['message']['text'],
            print chat['update_id'] > last_chat_id, chat['update_id'], last_chat_id
        if chat['update_id'] > last_chat_id:
            if user_id in message.keys():
                message[user_id].append(chat)
            else:
                message[user_id] = []
                message[user_id].append(chat)
            last_chat_id = chat['update_id']

    return message, last_chat_id

def userstep(db_connect):
    key = private.key
    get_chat = 'https://api.telegram.org/bot' + key + '/getUpdates'


    print get_chat
    chat_response = urllib2.urlopen(get_chat).read()
    chat_list = json.loads(chat_response)

    last_chat = get_latest_chat(db_connect)
    user_chat, l = parse_message(chat_list['result'], last_chat)

    put_messages(db_connect, user_chat)

    users = get_users(db_connect)
    new_users = []


    for i in chat_list['result']:
        if not contains_user(i['message']['chat']['id'], users) and not i['message']['chat']['id'] in new_users:
            new_users.append(i['message']['chat']['id'])
    if print_alert:
        print new_users
    if not test and len(new_users) > 0:
        put_users(db_connect, new_users)

    return users



def sendAlert(db_connect, now):
    cursor = db_connect.cursor()

    users = userstep(db_connect)

    # chat_id = chat_list['result'][1]['message']['chat']['id']
    rank, news, twit = parse()
    insert_news(db_connect, rank, news, twit)
    if print_alert:
        print "rank"
        print rank
        print news
        print 'news'
        for i in news:
            print i

    if(False):
        if print_alert:
            print users, users[0]
        return

    text = get_text(rank, news, twit, 3)
    raw_text = text
    if print_alert:
        print
        print raw_text.encode('utf-8')
        print

    # for i in users:
    # for i in chat_list['result']:
    # for i in chat_list['result']:
    for i in users:
        # chat_id = i['message']['chat']['id']
        # chat_id = 202959968
        chat_id = i['user_id']
        group_id = i['group_id']

        if group_id and group_id >= 0:# and group_id == 2:
            group_type = pgroup[int(group_id) - 1]['type']
            # text = get_text(rank, news, twit, group_type)
            text = get_notice(group_type)
            group_interval = pgroup[int(group_id) - 1]['interval']
            print group_id, i, ' | ', (compare_time(group_interval, now)), ' | '
            if (compare_time(group_interval, now)):
                # text_temp = str(group_id) + '\n' + text
                send_msg(chat_id, text)


    cursor.close()

def contains_user(user, users):
    for u in users:
        print user, ' with ', u['user_id']
        if user == u['user_id']:
            return True
    return False

def compare_time(interval, time):
    min = interval % 1
    hour = interval / 1
    rate = time.hour - startHour# + (startHour % 2)
    print rate % hour == 0, min == 0, rate % interval == 0
    if rate % hour == 0 and (min == 0 or rate % interval == 0):
        return True
    return False


def send_msg(chat_id, text):
    key = private.key
    text = urllib.quote(text.encode('utf-8'))
    url = 'https://api.telegram.org/bot' + key + '/sendMessage?chat_id=' + str(chat_id) + '&parse_mode=markdown&text=' + text
    print url
    # print "12 : ", chat_id in people12, "; 6 : ", chat_id in people6
    try:
        message = urllib2.urlopen(url).read()
        print message
    except urllib2.HTTPError:
        print "fail"


def timer():

    while True:
        db_connect = config.mjudb().getDB()
        now = datetime.now()
        if now > end_date and now < start_date:
            print start_date, ' : ', now, ':', end_date, "bye", now - end_date
            break
        print 'check : ', startHour <= now.hour <= endHour, (now.minute in [0]), now.minute
        if startHour <= now.hour <= endHour and (now.minute in [0]):
            print "send alert ", now
            sendAlert(db_connect, now)
        else:
            print "deep sleep ", now, " || [", startHour, "], [", endHour, "]"
        delay = 30 - now.minute % 30
        print "i can sleep ", delay, "minutes"
        time.sleep(sleep_sec * delay)
        db_connect.close()

        # if startHour <= now.hour <= endHour and (now.minute in [40, 41, 47, 48, 52, 54]): #For desktop
        # if startHour <= now.hour <= endHour and (now.minute in [30, 0, 39, 40, 41, 42, 43, 44, 45]): #For server
        #if startHour <= now.hour <= endHour and (now.minute in [30, 0]):#,10,20,40,50]): #For server
        # if startHour <= now.hour <= endHour ): #For server
        #     pass
        # else:
        #     print "sleep ", now
        #     time.sleep(sleep_sec)


def run(db_connect):
    timer()

    db_connect.close()

def test_get_message(db_connect = None):
    hour_offset = timedelta(hours=9)
    print datetime.utcfromtimestamp(1480738172) + hour_offset
    userstep(db_connect)


def test_parser():
    rank, news, twit = parse()
    print get_text(rank, news, twit, 1)
    print get_text(rank, news, twit, 2)
    print get_text(rank, news, twit, 3)


def test_sendmsg(db_connect):
    msgsend = True
    t = datetime(2016, 11, 11, 01, 0)
    print '----------------'
    print compare_time(1, t)
    print compare_time(2, t)
    if msgsend:
        sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 02, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 03, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 04, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 05, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 06, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 07, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 8, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 9, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 10, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)
    # t = datetime(2016, 11, 11, 11, 0)
    # print '----------------'
    # print compare_time(1, t)
    # print compare_time(2, t)
    # if msgsend:
    #     sendAlert(db_connect, t)

    db_connect.close()


if __name__ == "__main__":
    db_connect = config.mjudb().getDB()
    pgroup = get_group(db_connect)
    # db_connect.close()
    run(db_connect)

    # test_sendmsg(db_connect)
    # test_parser()
    # userstep(db_connect)
    # parseTweet("jtbc")
    # db_connect.close()
    # sendAlert(datetime.now())
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
