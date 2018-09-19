from web.get_data import get_alarminfo, check_alarm

from flask_mail import Mail, Message
from threading import Thread
from flask import current_app

# 异步发送预警email

def send_async_email(app=current_app):
    thr = Thread(target=send_email, args=[app])
    thr.start()

def send_email(app=current_app):
    lastest_alarm = get_alarminfo(False);
    mail = Mail(app)
    for single in lastest_alarm:
        # 如果污染物最新数据超过阈值
        result = check_alarm(single['site'], single['pollution'], single['value'])
        if (result['state'] == True):
            percent = '%.2f%%' % ((int(result['db_value'])-int(single['value']))/ int(single['value'])* 100)
            msg = Message(subject="@AirNet污染物预警！监测到" +"观测点："+single['site']+ "的污染物："+single['pollution'] + "已超标"+percent,
                          recipients=["753651042@qq.com"])
            msg.html = "<p>您好，这里是AirNet。</p><p>我们已监测到您设定的污染物：【" + single['pollution'] + "】已超过预警值：【" \
                       + str(single['value']) + "】</p><p>此次监测时间：【"+result['db_time']+"】，监测值为：【"+str(result['db_value'])+"】</p><p>感谢您对AirNet的支持</p>"
            mail.send(msg)
            # print("邮件发送成功");


