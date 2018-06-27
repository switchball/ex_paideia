#!/usr/bin/env python
# Three Thousand Thoughts
import random
import threading
import time
import json

from flask import Flask
from flask import Response
from flask import url_for
from flask import render_template

from books import BookExportingThread



exporting_threads = {}
app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    # template

    return render_template('index.html')
    #return 'task id: #%s' % thread_id

@app.route('/check_task')
def check():
    global exporting_threads
    ret = ""
    for key in exporting_threads:
        t = exporting_threads[key]
        s = 'alive' if t.isAlive() else 'dead'
        ret += f'Task #{key} -> {s}\n'
    return ret


@app.route('/run_task', methods=['POST'])
def run_task():
    global exporting_threads

    tid = -1
    # get running task
    for key in exporting_threads:
        t = exporting_threads[key]
        if t.isAlive():
            tid = key
            return tid


    if tid == -1:
        thread_id = random.randint(0, 10000)
        exporting_threads[thread_id] = BookExportingThread()
        exporting_threads[thread_id].start()
    else:
        thread_id = tid

    url_for('progress', thread_id=thread_id)

    return '%s' % thread_id


@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    global exporting_threads

    ret = {
        'progress': exporting_threads[thread_id].progress,
        'message': exporting_threads[thread_id].message
    }

    return Response(json.dumps(ret), mimetype='application/json')


if __name__ == '__main__':
    app.run()

# https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs