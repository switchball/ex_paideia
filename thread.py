import random
import threading
import time

from flask import Flask
from books import BookExportingThread



exporting_threads = {}
app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    global exporting_threads

    thread_id = random.randint(0, 10000)
    exporting_threads[thread_id] = BookExportingThread()
    exporting_threads[thread_id].start()

    return 'task id: #%s' % thread_id


@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    global exporting_threads

    return str(exporting_threads[thread_id].progress) + ":" + exporting_threads[thread_id].message


if __name__ == '__main__':
    app.run()

# https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs