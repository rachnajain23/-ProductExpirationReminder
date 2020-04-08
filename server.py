from datetime import datetime
from threading import Timer
import ReminderService
import time
while True:
    # x=datetime.today()
    # y=x.replace(day=x.day+1, hour=20, minute=55, second=0, microsecond=0)
    # delta_t=y-x
    ReminderService.notifyUsers()  # run at 9am
    time.sleep(7200)
    ReminderService.notifyUsers()  # run at 11am
    time.sleep(7200)
    ReminderService.notifyUsers()  # run at 1pm
    time.sleep(14400)
    ReminderService.notifyUsers()  # run at 5pm
    time.sleep(10800)
    ReminderService.notifyUsers()  # run at 8pm
    time.sleep(46800)
    # print(secs)
    # t = Timer(secs, ReminderService.notifyUsers())
    # t.start()
