import os
import requests
from flask import Flask, render_template, request, Response, jsonify
from flask.ext.assets import Environment, Bundle
from flask.ext.cors import CORS

app = Flask(__name__)
app.config['DEBUG'] = True if os.getenv("ENV", "DEBUG") is "PROD" else False
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


IN_TEST_MODE = int(os.getenv('TEST_MODE', 1)) == 1
LOB_AUTH = ('test_07fa45ae745b1d90e49e36ebb2112d6c128' if IN_TEST_MODE else os.getenv('LOB_API_KEY'), '')
STRIPE_AUTH = ('K4tdXzvrAYrt5gUpgzAdROuKjAt49usy' if IN_TEST_MODE else os.getenv('STRIPE_API_KEY'), '')



@app.route('/')
def home():
    return render_template('index.html', in_test=IN_TEST_MODE)

import pdb
@app.route('/send-letter', methods=['GET', 'POST'])
def send():
    data = request.form

    # process stripe charge
    token = data.get('token', None)
    if token:
        payload = {'amount':299, 'currency': 'usd', 'source': token, 'description': 'Sending 1 letter via owl'}
        auth = STRIPE_AUTH
        res = requests.post('https://api.stripe.com/v1/charges', data=payload, auth=STRIPE_AUTH)
        if res.status_code in [200, 201, 202]:
            
            senderAddress = verifyAddress(data['from-address'].strip(), data['from-location'].split(',')[0].strip(), data['from-location'].split(',')[1].strip())
            recipientAddress = verifyAddress(data['to-address'].strip(), data['to-location'].split(',')[0].strip(), data['to-location'].split(',')[1].strip())

            if not senderAddress or not recipientAddress:
                return jsonify({"success": False, "error": "Unable to verify your address."})

            sender = createAddress(data['from-name'], senderAddress)
            recipient = createAddress(data['to-name'], recipientAddress)

            if not sender or not recipient:
                return jsonify({"success": False, "error": "Unable to save your address."})

            full_letter = render_template("lob_base.html", message_html=data['html'])
            createdObj = createLobObject(full_letter)

            service = int(data['service'])

            job = sendLetter(recipient['id'], sender['id'], createdObj['id'], service)

            if not job:
                return jsonify({"success": False, "error": "Unable to send letter."})

            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Stripe authentication failed."})


def verifyAddress(address, city, state):
    payload = {'address_line1': address, 'address_city': city, 'address_state': state}
    res = requests.post('https://api.lob.com/v1/verify', data=payload, auth=LOB_AUTH)

    if res.json().has_key('address'):
        return res.json()['address']
    else:
        return None


def createAddress(name, address):
    payload = address
    payload['name'] = name
    payload.pop('object')

    res = requests.post("https://api.lob.com/v1/addresses", data=payload, auth=LOB_AUTH)

    return res.json()


def createLobObject(html):
    payload = {'setting': 100, 'template': 1, 'file': html}
 
    res = requests.post('https://api.lob.com/v1/objects', data=payload, auth=LOB_AUTH)

    return res.json()


def sendLetter(recipient, sender, object_id, service):
    payload = {'from': sender, 'to': recipient, 'object1': object_id}
    if service != 0:
        payload['service'] = service

    res = requests.post('https://api.lob.com/v1/jobs', data=payload, auth=LOB_AUTH)

    return res.json()


if __name__ == '__main__':
    app.run(host="0.0.0.0")
