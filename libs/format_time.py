import datetime

def format_time(time):
    time = str(time).replace(".000Z", "")
    time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    time += datetime.timedelta(hours=+8)
    time = time.replace(minute=0, second=0)
    return time

