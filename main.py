import os
from flask import Flask, render_template
from flask_funnel import Funnel

app = Flask(__name__)
app.debug = True
Funnel(app)
app.config['LESS_PREPROCESS'] = True

app.config['CSS_BUNDLES'] = {
    'index': (
        '//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/styles/default.min.css',
        'css/index.less',
    ),
}

app.config['JS_BUNDLES'] = {
    'index': (
        '//ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js',
        '//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/highlight.min.js',
        'js/markdown.min.js',
        'js/index.js',
    ),
}

@app.route('/')
def home():
    return render_template('index.html')