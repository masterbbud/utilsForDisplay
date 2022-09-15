from PIL import Image
from sklearn.cluster import KMeans
import requests
import random
from perlin_noise import PerlinNoise
import math
from queue_manager import HTTPSQueue
from time import sleep

currentMesh = []
numColors = 80
count = 50 # ???
colorspeed = 200 # how many seconds per cycle of perlin
moveweight = 250 # factor for move speed
changeTime = 10 # seconds
currentChange = None # seconds, up to changeTime

# DEPRECATED

def initialMesh():
    global currentMesh
    colors = []
    for _ in range(numColors):
        colors.append({
            'red': random.randrange(256),
            'green': random.randrange(256),
            'blue': random.randrange(256),
            'dred': 0,
            'dgreen': 0,
            'dblue': 0,
            'percentx': random.randrange(101),
            'percenty': random.randrange(101),
            'noisex': PerlinNoise(),
            'noisey': PerlinNoise()
        })
    currentMesh = colors
    return meshToCSS(colors)

def moveMesh(delta):
    global currentMesh, count, currentChange
    # Takes currentMesh and moves it just a bit, then returns
    offset = 0
    for color in currentMesh:
        color['percentx'] = color['noisex']((count+offset)/colorspeed)*moveweight + 30 + offset/colorspeed * 40
        color['percenty'] = color['noisey']((count+offset)/colorspeed)*moveweight + 30 + offset/colorspeed * 40
        color['red']      += color['dred'] * delta
        color['green']    += color['dgreen'] * delta
        color['blue']     += color['dblue'] * delta
        offset += colorspeed / numColors
    count += 1
    if currentChange is not None:
        if currentChange >= changeTime:
            currentChange = None
            for color in currentMesh:
                color['dred']   = 0
                color['dgreen'] = 0
                color['dblue']  = 0
        else:
            currentChange += delta
    return meshToCSS(currentMesh)

def meshToCSS(mesh):
    rules = []
    for color in mesh:
        rules.append('radial-gradient(circle at '+str(color['percentx'])+'% '+str(color['percenty'])+'%, '+colorToHex(color)+', transparent 5%)')
    grad = ','.join(rules)
    return f".mesh{{background-image: {grad} !important; background-color: black;}}"

def perlinTo0255(val):
    val += math.sqrt(2)/2
    val *= math.sqrt(2) * (255/2)
    return val

def colorToHex(color):
    return f"rgba({color['red']}, {color['green']}, {color['blue']}, 1)"

def getBestColors(url, num):
    img = Image.open(requests.get(url, stream=True).raw).resize((50,50))
    if img.mode != "RGB":
        img = img.convert("RGB")
    clt = KMeans(n_clusters=num)
    clt.fit(list(img.getdata()))
    return clt.cluster_centers_.tolist()

def setMeshColors(url):
    global currentMesh
    for color, newcolor in zip(currentMesh, getBestColors(url, numColors)):
        color['red']      = newcolor[0]
        color['green']    = newcolor[1]
        color['blue']     = newcolor[2]

def getMeshColors(url):
    tempMesh = []
    for newcolor in getBestColors(url, numColors):
        tempMesh.append({
            'red':   newcolor[0],
            'green': newcolor[1],
            'blue':  newcolor[2]
        })
    return tempMesh

def startChanging(url):
    global currentChange, currentMesh
    for old, new in zip(currentMesh, getMeshColors(url)):
        old['dred'] = (new['red'] - old['red']) / changeTime
        old['dgreen'] = (new['green'] - old['green']) / changeTime
        old['dblue'] = (new['blue'] - old['blue']) / changeTime
    currentChange = 0

def updates():
    while True:
        data = moveMesh(0.1)
        data = {
            'updatetype': 'mesh',
            'css': data
        }
        HTTPSQueue.add(data)
        sleep(0.1)
