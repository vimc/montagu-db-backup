#!/usr/bin/env python3
from datetime import datetime, timezone

from dateutil import parser
from subprocess import PIPE, run

from flask import Flask

from metrics import render_metrics

DATABASE_NAME = "montagu"
app = Flask(__name__)


def seconds_elapsed_since(timestamp):
    if timestamp:
        now = datetime.now()
        return (now - timestamp).total_seconds()
    else:
        return None


def parse_timestamp(raw):
    if raw and raw != "None":
        return parser.parse(raw)
    else:
        return None


def parse_status(text):
    lines = text.split("\n")
    raw_values = {}
    for line in lines[1:]:
        if line:
            print(line, flush=True)
            k, v = line.split(": ", 1)
            raw_values[k.strip()] = v.strip()

    last_available = parse_timestamp(raw_values["First available backup"])
    return {
        "barman_running": True,
        "barman_active": raw_values["Active"] == "True",
        "barman_pg_version": raw_values["PostgreSQL version"],
        "barman_available_backups": raw_values["No. of available backups"],
        "barman_time_since_last_backup_seconds": seconds_elapsed_since(
            last_available)
    }


@app.route('/metrics')
def metrics():
    result = run(["barman", "status", DATABASE_NAME],
                 stdout=PIPE, universal_newlines=True)
    if result.returncode == 0:
        ms = parse_status(result.stdout)
    else:
        ms = {"barman_running": False}
    return render_metrics(ms)
