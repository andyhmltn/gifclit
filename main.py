import pdb
import random
import gevent
from gevent import monkey
monkey.patch_all()
import requests
import bottle
import bottle_session
from bottle import route, run, get, post, request, response, static_file, template, error
from urllib import quote_plus
import json
from config import ACCT_KEY

ROOT_URI = 'https://api.datamarket.azure.com/Bing/Search/Image'


@route('/favicon.ico')
def favicon():
    return ''


@route('/about')
def home():
    with open('USAGE.TXT', 'r') as f:
        return "<pre>" + ''.join(f.readlines()) + "</pre>"


@route('/')
@route('/<query>')
def home(query=None):
    vhost = request.urlparts.netloc.split('.')[0]
    if vhost != 'gif':
        query = vhost
    response.set_header("Server", "GIF.CL.IT")
    request_uri = ROOT_URI + '?$format=json&Query=' + quote_plus("'"+query+" gif'")
    data = requests.get(request_uri, auth=(ACCT_KEY, ACCT_KEY))
    data = json.loads(data.text)['d']['results']
    max_attempts = len(data)-1
    attempts = 0
    serp_idx = 0
    good_image = False

    while not good_image:
        if data[serp_idx]['ContentType'] == "image/animatedgif" and \
           data[serp_idx]['Width'] >= 250 and \
           data[serp_idx]['Height'] >= 250 and \
           data[serp_idx]['FileSize'] >= 250000:
            good_image = True
        else:
            serp_idx = serp_idx + 1
            if attempts > max_attempts:
                return "None"

    return '<img style="margin:0;position:absolute;top:0;left:0;" src="' + data[serp_idx]['MediaUrl'] + '" />'


if __name__ == '__main__':
    app = bottle.app()
    session_plugin = bottle_session.SessionPlugin()
    app.install(session_plugin)
    app.run(host='0.0.0.0', port=9001, server='gevent', debug=False)
