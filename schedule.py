from datetime import datetime, time, timedelta
from time import sleep

import requests
from icalendar import Calendar, Event

from queue_manager import HTTPSQueue

classToColor = {
    'HIST': (163, 146, 118),
    'ENGL': (151, 197, 209),
    'MATH': (189, 100, 81),
    'CSCI': (98, 104, 156),
    'SWEN': (123, 201, 175),
    'SOIS': (205, 141, 227),
    'YOPS': (191, 230, 140)
}

calendarUrls = [
    "https://p44-caldav.icloud.com/published/2/NTA0OTAzMzExNTA0OTAzM62GB1NwkKVVT1g1Gxg_9JsNV4TGZpfAME-mYGfGLeyMngEig-1D2LU8J029Ql0SmCbO1J2KmQ6T1HVw_Dk6hv8",
    "https://p44-caldav.icloud.com/published/2/NTA0OTAzMzExNTA0OTAzM62GB1NwkKVVT1g1Gxg_9JsVazeYg6uGwhne4tFV8-US-BOxNZ42w5Ibbv2tjSxE_H1rnr8YvhdfKKai14u5P74",
    "https://p44-caldav.icloud.com/published/2/NTA0OTAzMzExNTA0OTAzM62GB1NwkKVVT1g1Gxg_9JsbUCLsj-K8Qx392jpZ7_TCM24EXPatMNcnKR7X1nor8M5WXBH0GkZWpUK7FyjGq6c",
    "https://p44-caldav.icloud.com/published/2/NTA0OTAzMzExNTA0OTAzM62GB1NwkKVVT1g1Gxg_9JuFcGCkE7GMpo8Xp-cAAI34",
    "https://p44-caldav.icloud.com/published/2/NTA0OTAzMzExNTA0OTAzM62GB1NwkKVVT1g1Gxg_9JtOkKfoe900FoN-W2jIdon1IfKETl1gcgHgDwLe-MuZ9TU81cLFrNm1KkPs-sljXaE"
]

events = []
eventBlocks = []

def getDailyEvents(urls):
    global events, eventBlocks

    todaysEvents = []

    for url in urls:
        text = requests.get(url).text
        if not text:
            return
        cal = Calendar.from_ical(text)
        for comp in cal.subcomponents:
            if 'WEEKLY' in comp.get('RRULE', {}).get('FREQ', []):
                if comp['DTSTART'].dt.weekday() == datetime.today().weekday():
                    todaysEvents.append(comp)
            elif isinstance(comp, Event):
                if ensureDate(comp['DTSTART'].dt) == datetime.today().date():
                    todaysEvents.append(comp)
    
    events = todaysEvents
    for event in events:
        if not isinstance(event['DTSTART'].dt, datetime):
            event['DTSTART'].dt = datetime.combine(event['DTSTART'].dt, time(0))
            event['DTEND'].dt = datetime.combine(event['DTEND'].dt, time(1))
            event['ISALLDAY'] = True
        else:
            event['ISALLDAY'] = False
    events.sort(key=lambda x: x['DTSTART'].dt.time())

    startTime = time(8)
    endTime   = time(22)

    eventBlocks = []

    for i in range(24*12):
        mins = i*5
        iTime = (datetime.combine(datetime.today(),time()) + timedelta(minutes=mins)).time()
        if iTime < startTime or iTime >= endTime:
            continue
        name = ''
        for c in events:
            if c['DTSTART'].dt.time() <= iTime and c['DTEND'].dt.time() > iTime:
                name = c['SUMMARY']
        if len(eventBlocks) == 0 or name != eventBlocks[-1]['name']:
            eventBlocks.append({'name': name, 'length': 1})
        else:
            eventBlocks[-1]['length'] += 1

def ensureDate(dt):
    if not isinstance(dt, datetime):
        return dt
    return dt.date()

def generateSchedule(urls):
    # DEPRECATED
    html = ''
    ct = 0
    getDailyEvents(urls)
    for item in eventBlocks:
        if item['name'] != '':
            ctuple = classToColor.get(item['name'][:4], (255,255,255))
            html += f'''<div class="sub-overlay" style="{gradientBackground(ctuple)} top: {ct+59}px; left: 50px; width: 100px; height: {item["length"]-2}px;"></div>\n'''
        ct += item['length']
    return html

def generateEventsList(urls):
    html = ''
    getDailyEvents(urls)
    highlightNext = False
    if not events:
        return
    if events[0]['DTSTART'].dt.time() > datetime.now().time():
        highlightNext = True
    htmlDict = []
    for item in events:
        currValue = {}
        dt = item['DTSTART'].dt
        if item['ISALLDAY']:
            currValue['highlighted'] = False
            currValue['description'] = item['SUMMARY']
            currValue['time'] = 'All Day'
        else:
            t1 = dt.strftime('%I:%M %p')
            if t1[0] == '0':
                t1 = t1[1:]
            t2 = item['DTEND'].dt.strftime('%I:%M %p')
            if t2[0] == '0':
                t2 = t2[1:]
            currValue['highlighted'] = highlightNext and dt.time() >= datetime.now().time()
            currValue['description'] = item['SUMMARY']
            currValue['time'] = f'{t1} - {t2}'
            highlightNext = dt.time() < datetime.now().time()
        htmlDict.append(currValue)
    start = 0
    end = len(htmlDict)
    if len(htmlDict) > 4:
        hIndex = 0
        for i, event in enumerate(htmlDict):
            if event['highlighted']:
                hIndex = i
                break
        scroll = 0
        while len(htmlDict) - hIndex - scroll > 3:
            scroll += 1
        start = len(htmlDict) - scroll - 4
        end = len(htmlDict) - scroll
    html = ''
    for i, item in enumerate(htmlDict):
        if i < start or i >= end:
            continue
        nextClass = ' highlighted-event' if item['highlighted'] else ''
        html += f'''<div class="single-event{nextClass}">'''
        html += f'''<div class="column-inline">'''
        html += f'''<div class="event-description">{item['description']}</div>\n'''
        html += f'''</div>'''
        html += f'''<div class="column-inline">'''
        html += f'''<div class="calendar-line" style="background-color: red"></div>\n'''
        html += f'''</div>'''
        html += f'''<div class="event-time">{item['time']}</div>\n'''
        html += f'''</div>'''
    return html

def gradientBackground(ctuple):
    return f'background: linear-gradient(135deg, rgb({ctuple[0]}, {ctuple[1]}, {ctuple[2]}), rgb({max(ctuple[0]-50,0)}, {max(ctuple[1]-50,0)}, {max(ctuple[2]-50,0)}));'

def updates():
    while True:
        data = {
            'updatetype': 'calendar',
            'html': generateEventsList(calendarUrls),
            'date': datetime.today().strftime('%B %d'),
            'weekday': datetime.today().strftime('%A')
        }
        if data['html']:
            for _ in range(2):
                HTTPSQueue.add(data)
        sleep(5*60)
