from datetime import datetime
from time import sleep

from queue_manager import HTTPSQueue


def updates():
    while True:
        timesend = datetime.now().strftime('%I:%M')
        if timesend[0] == '0':
            timesend = timesend[1:]
        data = {
            'updatetype': 'time',
            'time': timesend
        }
        HTTPSQueue.add(data)
        sleep(1)
