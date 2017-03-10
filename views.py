__author__ = "Jeremy Nelson"

import importlib
import os
import sqlite3
import sys
from app import app
from collections import OrderedDict
from flask import  abort, escape, jsonify, redirect, render_template 
from flask import make_response, request, session, url_for


JOBS = OrderedDict()
ROOT = os.path.abspath(os.path.dirname(__file__))
LIBS = os.path.join(ROOT, "lib")
sys.path.append(LIBS)
walker = next(os.walk(os.path.join(LIBS, "jobs")))
for filename in walker[2]:
    if filename.endswith("py") and not filename.startswith("_")\
        and not filename.startswith("ils"):
        name = filename.split(".")[0]
        module = importlib.import_module("jobs.{}".format(name), None)
        for row in dir(module):
            if row.endswith("Job"):
                job_class = getattr(module, row)
        JOBS[name] = {"module": module, "class": job_class, "name": name}

RECORD_TYPES = OrderedDict()
STATISTIC_TYPES = OrderedDict() 


def __setup__():
    global RECORD_TYPES, STATISTIC_TYPES
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    # Test if tables exist, load jobs.sql
    if len(cur.execute("SELECT * FROM SQLITE_MASTER;").fetchall()) < 1:
        with open(os.path.join(ROOT, "logs", "jobs.sql")) as fo:
            cur.executescript(fo.read())
        con.commit()
    rec_transaction = cur.execute(
        "SELECT id, name FROM RecordType ORDER BY name;")
    for row in rec_transaction.fetchall():
        RECORD_TYPES[row[1]] = row[0]
    stat_transaction = cur.execute(
        "SELECT id, name FROM StatisticType ORDER BY name;")
    for row in stat_transaction.fetchall():
        STATISTIC_TYPES[row[1]] = row[0]

def __add_note__(log_id, note):
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    cur.execute("INSERT INTO Notes (log_id, value) VALUES (?,?)",
        (log_id, note))
    con.commit()
    cur.close()
    con.close()


def __add_stat__(log_id, stat_id, value):
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    cur.execute("""INSERT INTO Statistics (log_id, stat_type_id, value) 
VALUES( ?,?,?);""",
        (log_id, stat_id, value))
    con.commit()
    cur.close()
    con.close()


def __get_log__(log_id):
    info = dict(id=log_id)
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    cur.execute("""SELECT Jobs.id, Jobs.created_on, Jobs.job_code, RecordType.name
FROM Jobs, RecordType WHERE Jobs.record_type_id=RecordType.id AND Jobs.id=?""", 
    (log_id, ))
    info["detail"] = cur.fetchone()
    info["job"] = JOBS[info["detail"][2]]
    cur.close()
    con.close()
    return info

def __get_logs__():
    logs = []
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    result = cur.execute("""SELECT Jobs.id, Jobs.created_on, Jobs.job_code, RecordType.name
FROM Jobs, RecordType WHERE Jobs.record_type_id=RecordType.id
ORDER BY Jobs.created_on;""")
    for row in result.fetchall():
        log_id = row[0]
        log = {"id": log_id,
               "created_on": row[1],
               "job": JOBS[row[2]]["module"].NAME,
               "notes": [],
               "record_type": row[3],
               "statistics": [] }
        notes_result = cur.execute("""SELECT created_on, value FROM Notes
WHERE log_id=?""", (log_id,))
        for note_row in notes_result.fetchall():
            log["notes"].append({"created_on": note_row[0],
                                 "value": note_row[1]})
        stats_result = cur.execute(
            """SELECT Statistics.created_on, StatisticType.name, Statistics.value
FROM Statistics, StatisticType
WHERE Statistics.stat_type_id = StatisticType.id AND Statistics.log_id=?
ORDER BY Statistics.created_on""",
            (log_id,))
        for stat_row in stats_result.fetchall():
            log["statistics"].append({"created_on": stat_row[0],
                                 "name": stat_row[1],
                                 "value": stat_row[2]})
        logs.append(log)
    cur.close()
    con.close()
    return logs
    
        


def __log_job__(code, form, raw_marc):
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    cur.execute("INSERT INTO jobs (job_code, input_marc, record_type_id) VALUES (?,?, ?)",
        (code, 
         raw_marc,
         form["record_type"]))
    log_id = cur.execute("SELECT max(id) FROM jobs").fetchone()[0]
    if len(form["notes"]) > 0:
        cur.execute("INSERT INTO Notes (log_id, value) VALUES (?,?)",
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
    

    
    

@app.route("/download/<status>/<log_id>.mrc")
def download(status, log_id):
    con = sqlite3.connect(os.path.join(ROOT, "logs", "jobs.sqlite"))
    cur = con.cursor()
    if status.startswith("mod"):
        result = cur.execute(
            "SELECT output_marc, job_code FROM Jobs WHERE id=?",
            (log_id,)).fetchone()
    if status.startswith("org"):
        result = cur.execute(
            "SELECT input_marc, job_code FROM Jobs WHERE id=?",
            (log_id,)).fetchone()
    if not result:
        abort(404)
    raw_file = result[0]
    job_code = result[1]
    response = make_response(raw_file)   
    cur.close()
    con.close()
    response.headers["Content-Disposition"] = \
        "attachment; filename={}-{}-{}.mrc".format(
            job_code,
            log_id,
            status)        
    return response

@app.route("/<code>", methods=["POST", "GET"])
def job(code):
    """Looks for code in JOBS. If GET returns form with Job class, if
    post, loads MARC21 into job and redirects to finished

    Args:
        code: Job code
    """
    if code in JOBS:
        if request.method.startswith("POST"):
            # Converts and returns transformed MARC
            job_class = JOBS[code]["class"]
            raw_marc = request.files["raw_marc_file"].stream.read() 
            log_id = __log_job__(code, request.form, raw_marc)
            if "collection" in request.form:
                job_instance = job_class(raw_marc, 
                                         collection=request.form['collection'])
            else:
                job_instance = job_class(raw_marc) 
            job_instance.load()
            __update_log__(log_id, job_instance)
            return redirect(url_for('finished', log_id=log_id))
        else:
            print(JOBS[code])
            return render_template(
                "start.html", 
                job=JOBS[code],
                jobs=JOBS.values(),
                rec_types=RECORD_TYPES,
                stat_types=STATISTIC_TYPES)
    else:
        abort(404)

@app.route("/finished")
@app.route("/finished/")
@app.route("/finished/<log_id>")
def finished(log_id=None):
    if not log_id:
        return render_template(
            "history.html",
            jobs=JOBS.values(),
            logs=__get_logs__())
    log_info = __get_log__(log_id)
    return render_template(
        "finished.html", 
        info=log_info,
        jobs=JOBS.values(),
        stat_types=STATISTIC_TYPES)

@app.route("/update", methods=["POST"])
def update():
    log_id = request.form["log_id"]
    for key, val in request.form.items():
        if key.startswith("stats"):
            stat_id = key.split("[")[-1].split("]")[0]
            __add_stat__(log_id, stat_id, val)
        if key.startswith("note") and len(val) > 0:
            __add_note__(log_id, val)      
    return "IN update"

@app.route("/")
def index():
    return render_template("index.html", jobs=JOBS.values())

if len(RECORD_TYPES) < 1 and len(STATISTIC_TYPES) < 1:
    __setup__()
