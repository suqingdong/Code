#!/usr/bin/env python
#-*- coding: utf-8 -*-

from smtplib import SMTP_SSL

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def sendEmail(text, email, contentType='plain'):
    # 登录认证
    smtp_server = 'smtp.exmail.qq.com'
    smtp_auth_username = 'humaninfo@novogene.com'
    smtp_auth_password = 'humandb0'
    smtp = SMTP_SSL(smtp_server)
    smtp.set_debuglevel(0)
    smtp.login(smtp_auth_username, smtp_auth_password)


    # 创建一个带附件的实例
    msg = MIMEMultipart()
    msg['Subject'] = '忘打卡提醒!'
    msg['From'] = 'me@wangdakale.com'
    msg['To'] = email

    # 添加邮件正文
    msg.attach(MIMEText(text, contentType, 'utf-8'))


    # 发送邮件
    smtp.sendmail('humaninfo@novogene.com', email, msg.as_string())
    smtp.quit()

    print('The mail has been successfully sent to %s!' % email)


if __name__ == '__main__':
    sendEmail('Hello world!', 'suqingdong@novogene.com')
