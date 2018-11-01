from libs.get_data import get_alarminfo, check_alarm
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from web import secure
from multiprocessing import Process

MAIL_SERVER = secure.MAIL_SERVER
MAIL_PORT = secure.MAIL_PORT
MAIL_USERNAME = secure.MAIL_USERNAME
MAIL_PASSWORD = secure.MAIL_PASSWORD


# 开启多进程异步发送E-mail
def send_async_email():
    try:
        process = Process(target=send_email())
        process.start()
    except Exception as e:
        raise e

def send_email():
    lastest_alarm = get_alarminfo(False)
    sender = MAIL_USERNAME
    sender_pass = MAIL_PASSWORD
    for single in lastest_alarm:
        # 如果污染物最新数据超过阈值
        result = check_alarm(single['site'], single['pollution'], single['value'])
        if (result['state'] == True):
            receiver = single['email']
            percent = '%.2f%%' % ((float(result['db_value']) - float(single['value'])) / float(single['value']) * 100)
            subject = "@AirNet污染物预警！监测到" + "观测点：" + single['site'] + "的污染物：" + single['pollution'] + "已超标" + percent
            mail_msg = "<p>您好，这里是AirNet。</p><p>我们已监测到您设定的污染物：【" + single['pollution'] + "】已超过预警值：【" \
                       + str(single['value']) + "】</p><p>此次监测时间：【" + result['db_time'] + "】，监测值为：【" + str(
                result['db_value']) + "】</p><p>感谢您对AirNet的支持</p>"
            message = MIMEText(mail_msg, 'html', 'utf-8')
            message['Subject'] = Header(subject, 'utf-8')
            message['From'] = sender
            message['To'] = receiver
            try:
                server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
                server.login(sender, sender_pass)
                server.sendmail(sender, receiver, message.as_string())
                print("Alarm mail send successful!")
            except Exception as e:
                print(e)
