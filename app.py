import threading

import flask

import clock
import mesh
import schedule
import spotify
import weather
from queue_manager import HTTPSQueue

app = flask.Flask(__name__)

@app.route('/')
def main():
    initializeThreads()
    return flask.render_template('template.html') + '<style id="mesh">'+mesh.initialMesh()+'</style>'

@app.route('/stream')
def stream():
    return flask.Response(HTTPSQueue.loop_read_queue(), mimetype='text/event-stream')

def initializeThreads():
    startThread(spotify.updates)
    startThread(mesh.updates)
    startThread(schedule.updates)
    startThread(clock.updates)
    startThread(spotify.keep_resetting_oauth)
    startThread(weather.updates)

def startThread(func):
    thread = threading.Thread(target=func, daemon=True)
    thread.start()
    updateThreads.append(thread)

if __name__ == "__main__":
    spotify.setup()
    updateThreads = []
    HTTPSQueue()
    app.run(port=5001, debug=False)
