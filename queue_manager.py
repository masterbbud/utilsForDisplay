import json
from queue import Queue
from time import sleep


class HTTPSQueue:

    HTTPSUpdateQueue = Queue()
    topOfQueue = None
    refresh = 0.05

    @staticmethod
    def add(message):
        HTTPSQueue.HTTPSUpdateQueue.put_nowait(message)

    @staticmethod
    def loop_read_queue():
        yield 'event: message\n'
        while True:
            sleep(HTTPSQueue.refresh)
            messages = HTTPSQueue.read_queue()
            msg = f'data: {json.dumps(messages)}\n\n'
            if len(messages):
                yield msg

    @staticmethod
    def read_queue():
        messages = []
        messageTypes = set()
        if HTTPSQueue.topOfQueue:
            messages.append(HTTPSQueue.topOfQueue)
            messageTypes.add(HTTPSQueue.topOfQueue['updatetype'])
            HTTPSQueue.topOfQueue = None
        while True:
            try:
                top = HTTPSQueue.HTTPSUpdateQueue.get_nowait()
            except:
                break
            if top['updatetype'] in messageTypes:
                HTTPSQueue.topOfQueue = top
                return messages
            messages.append(top)
            messageTypes.add(top['updatetype'])
        return messages
        