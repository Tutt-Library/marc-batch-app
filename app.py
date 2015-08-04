__author__ = "Jeremy Nelson"

import argparse
from flask import Flask 

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

from views import *

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
        app.run(host='localhost', port=20157, debug=True) 
