import json
import os
from time import sleep

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from mesh import moveMesh, startChanging
from queue_manager import HTTPSQueue

spotifyObject = None

token = None

currentSongData = {'name': '', 'shuffle': False, 'loop': 'off'}

def setup():
    global spotifyObject, token
    scope = 'user-read-playback-state'
    username = 'firh57c43suglzjugju1l89ph'

    configFile = open(os.path.join(os.getcwd(),"config.json"),'r')
    config = json.load(configFile)

    token = SpotifyOAuth(scope=scope,username=username,client_id=config['client_id'],client_secret=config['client_secret'],redirect_uri=config['redirect_uri'])
    
    refresh_token = token.cache_handler.get_cached_token()["refresh_token"]
    token.refresh_access_token(refresh_token)

    spotifyObject = spotipy.Spotify(auth_manager = token)

def getPlaybackState():
    data = spotifyObject.current_playback()
    if not data or not data.get('item'):
        return {}
    repeat = data.get('repeat_state')
    shuffle = data.get('shuffle_state')
    progress = data.get('progress_ms')
    length = data.get('item', {}).get('duration_ms')
    playing = data.get('is_playing')
    album = data.get('item', {}).get('album', {}).get('name')
    cover = data.get('item', {}).get('album', {}).get('images', [{}])[0].get('url')
    artists = []
    for a in data.get('item', {}).get('artists', []):
        artists.append(a.get('name'))
    artists = ', '.join(artists)
    name = data.get('item', {}).get('name')

    queue = spotifyObject.user_queue()
    newcover = None
    if queue and queue.get('queue'):
        newcover = queue.get('queue', [{}])[0].get('album', {}).get('images', [{}])[0].get('url')
        
    return {
        'name': name,
        'artists': artists,
        'album': album,
        'playing': playing,
        'progress': progress,
        'length': length,
        'shuffle': shuffle,
        'loop': repeat,
        'cover': cover,
        'nextcover': newcover
    }

def pausePath():
    return '<path d="M2.7 1a.7.7 0 00-.7.7v12.6a.7.7 0 00.7.7h2.6a.7.7 0 00.7-.7V1.7a.7.7 0 00-.7-.7H2.7zm8 0a.7.7 0 00-.7.7v12.6a.7.7 0 00.7.7h2.6a.7.7 0 00.7-.7V1.7a.7.7 0 00-.7-.7h-2.6z"></path>'

def playPath():
    return '<path d="M3 1.713a.7.7 0 011.05-.607l10.89 6.288a.7.7 0 010 1.212L4.05 14.894A.7.7 0 013 14.288V1.713z"></path>'

def pathForPlaying(playing):
    if playing:
        return pausePath()
    return playPath()

def updates():
    global currentSongData, sendSpotify
    while True:
        pback = getPlaybackState()
        if len(pback) == 0:
            return []
        data = {
            'updatetype': 'spotify',
            'state': pback.get('playing'),
            'progress': msToTime(pback.get('progress')),
            'progressx': calcProgressX(pback.get('progress'),pback.get('length'))
        }
        d2 = {}
        if currentSongData.get('name') != pback.get('name') or sendSpotify:
            sendSpotify = False
            if currentSongData.get('cover') != pback.get('cover'):
                startChanging(pback.get('cover'))
            currentSongData.update({
                'name': pback.get('name'),
                'cover': pback.get('cover')
            })
            data.update({
                'albumcover': pback.get('cover'),
                'name': pback.get('name'),
                'artist': pback.get('artists'),
                'album': pback.get('album'),
                'length': msToTime(pback.get('length'))
            })
            d2 = {
                'updatetype': 'mesh',
                'css': moveMesh(0)
            }
        if currentSongData.get('nextcover') != pback.get('nextcover'):
            currentSongData.update({
                'nextcover': pback.get('nextcover')
            })
            data.update({
                'nextcover': pback.get('nextcover')
            })
        if currentSongData.get('shuffle') != pback.get('shuffle'):
            currentSongData.update({
                'shuffle': pback.get('shuffle')
            })
            data.update({
                'shuffle': pback.get('shuffle')
            })
        if currentSongData.get('loop') != pback.get('loop'):
            currentSongData.update({
                'loop': pback.get('loop')
            })
            data.update({
                'loop': pback.get('loop')
            })
        if len(data) > 4:
            for _ in range(3):
                HTTPSQueue.add(data)
                if d2:
                    HTTPSQueue.add(d2)
        else:
            HTTPSQueue.add(data)
        sleep(0.2)

def calcProgressX(prog, length):
    return str(220 * prog / length-6)+'px'

def msToTime(ms):
    seconds = int((ms/1000) % 60)
    if seconds < 10:
        seconds = '0'+str(seconds)
    minutes = int((ms/60000))
    return f'{minutes}:{seconds}'

def keep_resetting_oauth():
    while True:
        sleep(60*60*24)
        refresh_token = token.cache_handler.get_cached_token()["refresh_token"]
        token.refresh_access_token(refresh_token)
