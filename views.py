__author__ = "Jeremy Nelson"

import importlib
import os
import sys
from app import app
from collections import OrderedDict
from flask import  abort, escape, jsonify, redirect, render_template 
from flask import request, session, url_for


JOBS = OrderedDict()
ROOT = os.path.abspath(os.path.dirname(__file__))
LIBS = os.path.join(ROOT, "lib")
sys.path.append(LIBS)
walker = next(os.walk(os.path.join(LIBS, "jobs")))
for filename in walker[2]:
    if filename.endswith("py") and not filename.startswith("_"):
        name = filename.split(".")[0]
        module = importlib.import_module("jobs.{}".format(name), None)
        JOBS[name] = {"class": module, "name": name}


@app.route("/<code>")
def job(code):
    if code in JOBS:
        return "Job is {}".format(code)
    else:
        abort(404)

@app.route("/")
def index():
    return render_template("index.html", jobs=JOBS.values())
