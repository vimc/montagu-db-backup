#!/usr/bin/env python3
import os
from datetime import datetime
from subprocess import PIPE, run

from dateutil import parser
from flask import Flask

from .montagu_metrics.metrics import label_metrics, render_metrics

app = Flask(__name__)


def get_db_name():
    return os.environ['BARMAN_DATABASE_NAME']


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


def without_first_line(text):
    return text.split("\n")[1:]


def barman_output_as_dict(text):
    lines = text.split("\n")[1:]
    raw_values = {}
    for line in lines:
        if line:
            print(line, flush=True)
            k, v = line.split(": ", 1)
            raw_values[k.strip()] = v.strip()
    return raw_values


def parse_status(status, check):
    status_values = barman_output_as_dict(status)
    check_values = barman_output_as_dict(check)

    last_available = parse_timestamp(status_values["Last available backup"])
    since_last_backup = seconds_elapsed_since(last_available)
    check_all_ok = all(x.startswith("OK") for x in check_values.values())

    return {
        "barman_running": True,
        "barman_ok": status_values["Active"] == "True" and check_all_ok,
        "barman_pg_version": status_values["PostgreSQL version"],
        "barman_available_backups": status_values["No. of available backups"],
        "barman_time_since_last_backup_seconds": since_last_backup,
        "barman_time_since_last_backup_minutes":
            since_last_backup / 60 if since_last_backup is not None else None,
        "barman_time_since_last_backup_hours":
            since_last_backup / 3600 if since_last_backup is not None else None,
        "barman_time_since_last_backup_days":
            since_last_backup / (3600 * 24) if since_last_backup is not None else None
    }


@app.route('/metrics')
def metrics():
    try:
        db_name = get_db_name()
        status = run(["barman", "status", db_name],
                     stdout=PIPE, universal_newlines=True)
        check = run(["barman", "check", db_name],
                     stdout=PIPE, universal_newlines=True)
        ms = parse_status(status.stdout, check.stdout)
        ms = label_metrics(ms, {"database": db_name})
        return render_metrics(ms)
    except:
        return render_metrics({
            "barman_responding": False
        })
