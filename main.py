import os
import requests
from flask import Flask, render_template, request, Response
from flask.ext.assets import Environment, Bundle
from html2canvasproxy import *

app = Flask(__name__)
app.config['DEBUG'] = True #True if os.getenv("ENV", "DEBUG") is "PROD" else False
assets = Environment(app)

js_base = Bundle('external/jquery.min.js',
            'external/highlight/highlight.min.js',
            'external/flat-ui/flat-ui-pro.min.js',
            filters='jsmin', output='gen/base.js')
js_index = Bundle('js/index.js', 'js/markdown.min.js',
            'external/html2canvas-0.4.1.js',
            output='gen/index.js')

assets.register('js_base', js_base)
assets.register('js_index', js_index)

css_base = Bundle('external/bootstrap.min.css',
                'external/flat-ui/flat-ui-pro.min.css',
                filters='cssmin', output='gen/base.css')

css_index = Bundle('external/highlight/default.min.css',
                Bundle('css/index.less', filters='less'),
                filters='cssmin', output='gen/index.css')

assets.register('css_base', css_base)
assets.register('css_index', css_index)

h2c = None
real_path = os.path.dirname(os.path.realpath(__file__)) + '/tmp'
virtual_path = '/html2canvas/static'

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/send-letter', methods=['GET', 'POST'])
def send():
    data = request.form

    sender = {'name': data['from-name'], 'address': data['from-address'], 'city': data['from-location'] }
    recipient = {'name': data['to-name'], 'address': data['to-address'], 'city': data['to-location'] }

    createdObject = createLobObject(data['html'])
    raise ValueError(createdObject)


def createLobObject(html):
    payload = {'setting': 100, 'template': 1}
    auth = ('test_07fa45ae745b1d90e49e36ebb2112d6c128', '')

    tempFile = TemporaryFile()
    tempFile.write(html)

    files = {"file": ('upload.html', html, 'text/html')}
 
    res = requests.post('https://api.lob.com/v1/objects', data=payload, auth=auth, files=files)
    return res.json()


@app.route('/html2canvas-proxy')
def html2canvas_proxy():
    h2c = html2canvasproxy(request.args.get('callback'), request.args.get('url'))

    h2c.enableCrossDomain()

    h2c.userAgent(request.headers['user_agent'])
    h2c.hostName(request.url)

    if request.referrer is not None:
        h2c.referer(request.referrer)

    h2c.route(real_path, virtual_path)

    if request.args.get('debug_vars'):
        return Response(str(h2c.debug_vars()), mimetype='text/plain')

    r = h2c.result()

    return Response(r['data'], mimetype=r['mime'])


@app.route('/html2canvas/static/<image>')
def images(image):
    res = html2canvasproxy.resource(real_path, image)

    if res is None:
        return '', 404
    else:
        return Response(res['data'], mimetype=res['mime'])


if __name__ == '__main__':
    app.run(host="0.0.0.0")
