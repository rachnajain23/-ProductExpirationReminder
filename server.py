from datetime import datetime
from threading import Timer
import Service
import time
while True:
    # x=datetime.today()
    # y=x.replace(day=x.day+1, hour=20, minute=55, second=0, microsecond=0)
    # delta_t=y-x
    Service.notifyUsers()  # run at 9am
    time.sleep(7200)
    Service.notifyUsers()  # run at 11am
    time.sleep(7200)
    Service.notifyUsers()  # run at 1pm
    time.sleep(14400)
    Service.notifyUsers()  # run at 5pm
    time.sleep(10800)
    Service.notifyUsers()  # run at 8pm
    Service.deleteOld()
    time.sleep(46800)
    # print(secs)
    # t = Timer(secs, ReminderService.notifyUsers())
    # t.start()
