import json
import os
from datetime import datetime
from time import sleep

import requests

from queue_manager import HTTPSQueue

configFile = open(os.path.join(os.getcwd(),"config.json"),'r')
config = json.load(configFile)

api_key = config['weather_api']

forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat=43.08&lon=-77.67&appid={api_key}"
current_url = f"http://api.openweathermap.org/data/2.5/weather?lat=43.08&lon=-77.67&appid={api_key}"

iconDict = {
    '01d': '01n',
    '02d': '02n',
    '03d': '03n',
    '04d': '02n',
    '09d': '10n',
    '10d': '10n',
    '11d': '11n',
    '13d': '13n',
    '50d': '50n'
}

def getCurrentWeather():
    response = requests.get(current_url)
    i = response.json()
    if i["cod"] != "404":
        if i['weather']:
            return {
                'temp': str(int((9/5) * (float(i['main']['temp']) - 273.15) + 32)) + chr(176),
                'weather': i['weather'][0]['main'],
                'description': i['weather'][0]['description'],
                'icon': generateIconLink(i['weather'][0]['icon'])
            }
        else:
            return {
                'temp': str(int((9/5) * (float(i['main']['temp']) - 273.15) + 32)) + chr(176)
            }
    return {}

def getDailyWeather():
    response = requests.get(forecast_url)
    x = response.json()
    retList = []
    if x["cod"] != "404":
        for i in x['list'][:4]:
            if i['weather']:
                retList.append({
                    'time': datetime.fromtimestamp(i['dt']).strftime("%I:%M").lstrip('0'),
                    'temp': str(int((9/5) * (float(i['main']['temp']) - 273.15) + 32)),
                    'weather': i['weather'][0]['main'],
                    'description': i['weather'][0]['description'],
                    'icon': generateIconLink(i['weather'][0]['icon'])
                })
            else:
                retList.append({
                    'time': datetime.fromtimestamp(i['dt']).strftime("%I:%M").lstrip('0'),
                    'temp': str(int((9/5) * (float(i['main']['temp']) - 273.15) + 32))
                })
    return retList

def generateIconLink(icon):
    return f"http://openweathermap.org/img/wn/{iconDict.get(icon, icon)}@2x.png"

def updates():
    while True:
        data = {
            'updatetype': 'weather',
            'dicts': []
        }
        data['dicts'].append(getCurrentWeather())
        data['dicts'] += getDailyWeather()
        for _ in range(3):
            HTTPSQueue.add(data)
        sleep(60)
