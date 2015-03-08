import os
from flask import Flask, render_template
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)
app.debug = True if os.getenv("ENV", "DEBUG") is "PROD" else False
assets = Environment(app)

js_base = Bundle('external/jquery.min.js',
            'external/highlight/highlight.min.js',
            filters='jsmin', output='gen/base.js')
js_index = Bundle('js/index.js', 'js/markdown.min.js',
            filters='jsmin', output='gen/index.js')

assets.register('js_base', js_base)
assets.register('js_index', js_index)

css_index = Bundle('external/highlight/default.min.css',
                Bundle('css/index.less', filters='less'),
                filters='cssmin', output='gen/index.css')
assets.register('css_index', css_index)

@app.route('/')
def home():
    return render_template('index.html')