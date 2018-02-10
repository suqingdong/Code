#!/usr/bin/env python
#-*- encoding: utf-8 -*-


import requests
import json
import datetime
import argparse
import sys
import string

from sendEmail import sendEmail



# solve coding problem
reload(sys)
sys.setdefaultencoding('utf8')


configDict = {
    'login_url': 'http://kq.novogene.com:8080/selfservice/login/',
    'search_url': 'http://kq.novogene.com:8080/selfatt/grid/selfatt/CardTimes/',
    'headers': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}
}

mailTemplate = string.Template('''Hey, ${name}:\n
    You might forget to punch card at ${card_date}!
    Your card records: ${clockInTime}\n
Bye~''')



def login(username, password):
    login_url = configDict.get('login_url')
    headers = configDict.get('headers')
    login_data = {
        'username': username,
        'password': password
    }
    session = requests.session()
    response = session.post(login_url, headers=headers, data=login_data)
    if response.text == 'ok':
        print('Login Successfully for %s!' % username)
        return session
    print('Login Failed! Check your username(work number) or password and try again.')
    exit(1)


def search(session, startTime, endTime, email, rp):
    search_url = configDict.get('search_url')
    headers = configDict.get('headers')
    search_data = {
        'ComeTime': startTime,
        'EndTime': endTime,
        'rp':rp
    }
    response = session.post(search_url, verify=False, headers=headers, data=search_data)
    result = json.loads(response.text)
    print('Name\tCardDate\tTimes\tClockInTime')
    
    nowHour = int(getTime('%H'))
    nowDay = int(getTime('%m%d'))

    lastDay = None
    name = 'you'
    
    for row in  result.get('rows'):
        name = row.get('name')
        card_date = row.get('card_date')
        times = row.get('times')
        clockInTime = row.get('ClockInTime').strip(',')
        print('%s\t%s\t%s\t%s' % (name, card_date, times, clockInTime))

        clockList = clockInTime.split(',')
        firstHour = int(clockList[0][:2])
        lastHour = int(clockList[-1][:2])

	lastDay = int(card_date[-5:-3]+card_date[-2:]) # 当条记录的day，不是昨天

        # 当天18点之后少打卡 或 之前任意时间少打卡 
        if (( firstHour>10 or lastHour<18 ) and nowHour>18 and nowDay==lastDay) or ( ( firstHour>10 or lastHour<18 ) and lastDay<nowDay ):
            text = mailTemplate.safe_substitute(name=name, card_date=card_date, clockInTime=clockInTime)
            print(text)
	    if email:
                sendEmail(text, email)

    # 周一至周五，如果没有当天的打开记录也会提醒
    week = getTime('%w')
    if (not lastDay) and (week in '12345') and ( lastDay < nowDay):
        text = 'Hey, %s:\n\nYou might forget to punch card this morning(%s).\n\nBye~' % (name, getTime())
        print(text)
	if email:
	    sendEmail(text, email)
    



def getTime(timeFormat='%Y-%m-%d', delta=0):
    d = datetime.datetime.now() + datetime.timedelta(days=delta)
    return d.strftime(timeFormat)




def main(username, password, startTime, endTime, email, rp):
    session = login(username, password)
    search(session, startTime=startTime, endTime=endTime, email=email, rp=rp)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='kq', usage='%(prog)s [options]', description='Check your card records. Contact: suqingdong@novogene.com')
    parser.add_argument('-u', '--username', dest='username', help='Your username[work number].', required=True)
    parser.add_argument('-p', '--password', dest='password', help='Your password[default="%(default)s"].', default='123456')
    parser.add_argument('-start', '--startTime', dest='startTime', help='Start time of searching.')
    parser.add_argument('-end', '--endTime', dest='endTime', help='End time of searching.')
    parser.add_argument('-delta', '--days', dest='delta',type=int, help='The last N days for searching[default=%(default)s].', default=-1)
    parser.add_argument('-em', '--email', dest='email', help='The email address for reciving.')
    parser.add_argument('-rp', '--total', dest='rp', help='The max number of records[default=%(default)s].', default=100)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0', help='Show the version.')
    args = vars(parser.parse_args())

    username = args.get('username')
    password = args.get('password')

    delta = args.get('delta')

    startTime = args.get('startTime') or getTime(delta=delta)
    endTime = args.get('endTime') or getTime()

    email = args.get('email')

    rp = args.get('rp')


    main(username, password, startTime, endTime, email, rp)


