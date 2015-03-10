import os
import requests
from flask import Flask, render_template, request, Response
from flask.ext.assets import Environment, Bundle
from flask.ext.cors import CORS

app = Flask(__name__)
app.config['DEBUG'] = True #True if os.getenv("ENV", "DEBUG") is "PROD" else False
assets = Environment(app)
cors = CORS(app, allow_headers="Content-Type")

js_base = Bundle('external/jquery.min.js',
            'external/highlight/highlight.min.js',
            'external/flat-ui/flat-ui-pro.min.js',
            filters='jsmin', output='gen/base.js')
js_index = Bundle('js/index.js', 'js/markdown.min.js',
            output='gen/index.js')

assets.register('js_base', js_base)
assets.register('js_index', js_index)

css_base = Bundle('external/bootstrap.min.css',
                'external/flat-ui/flat-ui-pro.min.css',
                'external/highlight/default.min.css',
                filters='cssmin', output='gen/base.css')

css_index = Bundle(Bundle('css/index.less', filters='less'),
                filters='cssmin', output='gen/index.css')

assets.register('css_base', css_base)
assets.register('css_index', css_index)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/send-letter', methods=['GET', 'POST'])
def send():
    data = request.form

    sender = {'name': data['from-name'], 'address': data['from-address'], 'city': data['from-location'] }
    recipient = {'name': data['to-name'], 'address': data['to-address'], 'city': data['to-location'] }

    full_letter = render_template("lob_base.html", message_html=data['html'])
    createdObj = createLobObject(full_letter)

    # return true or false based on whether the address is valid
    has_from_address = verifyAddress(data['from-address'], data['from-location'].split(',')[0], data['from-location'].split(',')[1])
    has_to_address = verifyAddress(data['to-address'], data['to-location'].split(',')[0], data['to-location'].split(',')[1])

    return has_from_address and has_to_address


def verifyAddress(address, city, state):
    auth = ('test_07fa45ae745b1d90e49e36ebb2112d6c128', '')
    payload = {'address_line1': address, 'address_city': city, 'address_state': state}
    res = requests.post('https://api.lob.com/v1/verify', data=payload, auth=auth)

    if res.json().has_key('address'):
        return res.json()['address']
    else:
        return None


def createLobObject(html):
    payload = {'setting': 100, 'template': 1, 'file': html}
    auth = ('test_07fa45ae745b1d90e49e36ebb2112d6c128', '')
 
    res = requests.post('https://api.lob.com/v1/objects', data=payload, auth=auth)

    return res.json()


if __name__ == '__main__':
    app.run(host="0.0.0.0")
