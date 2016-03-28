__author__ = "Jeremy Nelson"

import importlib
import os
import sqlite3
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
    if filename.endswith("py") and not filename.startswith("_")\
        and not filename.startswith("ils")\
        and not filename.endswith("_base.py"):
        name = filename.split(".")[0]
        module = importlib.import_module("jobs.{}".format(name), None)
        for row in dir(module):
            if row.endswith("Job"):
                job_class = getattr(module, row)
        JOBS[name] = {"module": module, "class": job_class, "name": name}


def __get_log__(log_id):
    info = dict()
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    cur.execute("SELECT * FROM Jobs WHERE id=?", (log_id, ))
    info["detail"] = cur.fetchone()
    info["job"] = JOBS[info["detail"][2]]
    cur.close()
    con.close()
    return info

def __log_job__(code, form, raw_marc):
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    cur.execute("INSERT INTO jobs (job_code, input_marc, record_type) VALUES (?,?, ?)",
        (code, 
         raw_marc,
         form["record_type"]))
    log_id = cur.execute("SELECT max(id) FROM jobs").fetchone()[0]
    if len(form["notes"]) > 0:
        cur.execute("INSERT INTO notes (log_id, note) VALUES (?,?)",
            (log_id, form["notes"]))
    con.commit()
    cur.close()
    con.close()
    return log_id

def __update_log__(log_id, job_instance):
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    cur.execute("UPDATE Jobs SET output_marc=? WHERE id=?",
        (job_instance.output(),
         log_id))
    con.commit()
    cur.close()
    con.close()
    

@app.route("/<code>", methods=["POST", "GET"])
def job(code):
    if code in JOBS:
        if request.method.startswith("POST"):
            # Converts and returns transformed
            job_class = JOBS[code]["class"]
            raw_marc = request.files["raw_marc_file"].stream.read() 
            log_id = __log_job__(code, request.form, raw_marc)
            job_instance = job_class(raw_marc)
            job_instance.load()
            __update_log__(log_id, job_instance)
            return redirect(url_for('finished', log_id=log_id))
        else:
            return render_template(
                "start.html", 
                job=JOBS[code],
                jobs=JOBS.values())
    else:
        abort(404)

@app.route("/finished")
@app.route("/finished/<log_id>")
def finished(log_id=None):
    if not log_id:
        return "Should display history"
    log_info = __get_log__(log_id)
    return render_template(
        "finished.html", 
        info=log_info,
        jobs=JOBS.values())

@app.route("/")
def index():
    return render_template("index.html", jobs=JOBS.values())
