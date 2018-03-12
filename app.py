__author__ = "Jeremy Nelson"

import argparse
from flask import Flask 
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

from views import *

parent_app = DispatcherMiddleware(
    app,
    {"/marc21-batch": app}
)

# Main handler
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['run'],
        help='Action choices: run')
    args = parser.parse_args()
    if args.action.startswith('run'):
        print("Running application in debug mode")
        app.run(host='0.0.0.0', port=20157, debug=True) 
