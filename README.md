# snail-mail
Send snail mail easily.

You can visit this website at http://easy-snail-mail.herokuapp.com/

### Local Setup

###### Requirements
- Python 2.7+
- virtualenv
- npm

```sh
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ npm install -g less
$ foreman run python main.py
```

You can now view a local instance at http://localhost:5000/

Please note that if you make your `venv` folder within this project's root directory, you'll need to add `venv/` to `.gitignore`.
