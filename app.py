# all the imports
import os
import sqlite3
import uuid
import time
import json
from time import strftime
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from logging.handlers import RotatingFileHandler
import logging 

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py


@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')

        log = {}

        log['timestamp'] = int(time.time())
        log['datetime'] = ts 
        log['headers'] = dict(request.headers)
        log['method'] = request.method
        log['src_ip'] = request.remote_addr
        log['path'] = request.path
        log['uri_root'] = request.url_root
        log['args'] = request.args
        log['host'] = request.host

        if request.is_json:
            log['json'] = request.json


        logger.error(json.dumps(log))
    return response

@app.route('/', methods=['GET'])
def index():
    trap_args = []
    x = 0
    y = 0
    uuid = ''


    # Get the x and y variables from the bot trap
    if request.args.get('x') is not None:
        x = str(request.args.get('x'))

    if request.args.get('y') is not None:
        y = str(request.args.get('y'))

    # Get updates bot trap args
    trap_args = genTrapArgs(x, y)

    # Get uuid
    if request.args.get('uuid') is not None:
        uuid = str(request.args.get('uuid'))


    if request.args.get('js') is not None:
        print(request.args.get('js'))
        if request.args.get('js') == 'True':
            js = True
        else:
            js = False
    else:
        js = None

    return render_template('index.html', 
                            trap_args=trap_args, 
                            uuid=genUUID(uuid), 
                            checkjs=genCheckJs(x, js), 
                            root_url=request.host_url,
                            checkImg=checkImg(x),
                            js=js
    )

# TODO: 301 checking and 302 redirect
@app.route('/<path:path>', methods=['HEAD', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'POST', 'CONNECT'])
@app.route('/<path:path>')
def catchAll(path):
    #print(path)
    tests = []

    # Image test
    tests.append({"tag": "gets_images", "path": "img.jpg"})

    # xhr test
    tests.append({"tag": "sends_xhr", "path": "xhr"})

    # Check tests
    for test in tests:
        if test['path'] in path:
            logTag(test['tag'], request)

    return "OK"


def logTag(tag, request):
    ts = strftime('[%Y-%b-%d %H:%M]')

    log = {}

    log['timestamp'] = int(time.time())
    log['datetime'] = ts 
    log['src_ip'] = request.remote_addr
    log['tag'] = tag

    tagger.error(json.dumps(log))

def checkImg(x):
    if x == 0:
        return True
    else:
        return False

# TODO: Checkjs should be more of a structured object with parameters, potentially passing the UUID
def genCheckJs(x, js=None):

    return (x == 0 and js is None)

def genTrapArgs(x, y):
    ret = []

    if x == 0:
        x = ""
    else:
        x += ","

    for i in range (1, 6):
        ret.append({'x': x+str(y), 'y': i})

    return ret

def genUUID(theuuid):
    # TODO: Save this UUID so we can look for it later
    if len(theuuid) < 1:
        retuuid = str(uuid.uuid4())

        ts = strftime('[%Y-%b-%d %H:%M]')

        log = {}

        log['timestamp'] = int(time.time())
        log['datetime'] = ts 
        log['src_ip'] = request.remote_addr
        log['uuid'] = retuuid

        uuids.error(json.dumps(log))

        return retuuid
    else:
        return theuuid

if __name__ == "__main__":
    
    # Request logger
    handler = RotatingFileHandler('http.log', maxBytes=5000000, backupCount=3)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    # Tag logger
    tag_handler = RotatingFileHandler('tags.log', maxBytes=5000000, backupCount=3)
    tagger = logging.getLogger('tags')
    tagger.setLevel(logging.ERROR)
    tagger.addHandler(tag_handler)

    # UUIDS
    tag_handler = RotatingFileHandler('uuids.log', maxBytes=5000000, backupCount=3)
    uuids = logging.getLogger('uuids')
    uuids.setLevel(logging.ERROR)
    uuids.addHandler(tag_handler)


    if 'PORT' in os.environ:
        PORT = int(os.environ['PORT'])
    else:
        PORT = 8080

    if 'SSL_CONTEXT' in os.environ:
        if os.environ['SSL_CONTEXT'] == 'adhoc':
            SSL_CONTEXT = 'adhoc'
    else:
        SSL_CONTEXT = None

    app.secret_key = 'jw6bw48bw4vuse5iwb5iwr6biw5e6isjzvertgrs6ibw6iwv5eacyrzhvdybksuvayctahsjdkynluobi6uwv5ey'

    app.run(port=PORT, ssl_context=SSL_CONTEXT, host='0.0.0.0')

