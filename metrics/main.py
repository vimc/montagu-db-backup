#!/usr/bin/env python3
import os
from datetime import datetime
from subprocess import PIPE, run

from dateutil import parser
from flask import Flask

from metrics import render_metrics, label_metrics

DATABASE_NAME = os.environ['BARMAN_DATABASE_NAME']
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


def without_first_line(text):
    return text.split("\n")[1:]


def parse_status(status, check):
    lines = without_first_line(status) + without_first_line(check)
    raw_values = {}
    for line in lines:
        if line:
            print(line, flush=True)
            k, v = line.split(": ", 1)
            raw_values[k.strip()] = v.strip()

    last_available = parse_timestamp(raw_values["Last available backup"])
    since_last_backup = seconds_elapsed_since(last_available)
    ok = check_booleans(raw_values, [
        "Active", "PostgreSQL", "PostgreSQL_streaming", "wal_level",
        "replication slot", "directories", "retention policy settings",
        "compresion settings", "failed backups", "pg_basebackup",
        "pg_basebackup")

    return {
        "barman_running": True,
        "barman_ok": raw_values["Active"] == "True",
        "barman_pg_version": raw_values["PostgreSQL version"],
        "barman_available_backups": raw_values["No. of available backups"],
        "barman_time_since_last_backup_seconds": since_last_backup,
        "barman_time_since_last_backup_minutes": since_last_backup / 60,
        "barman_time_since_last_backup_hours": since_last_backup / 3600,
        "barman_time_since_last_backup_days": since_last_backup / (3600 * 24)
    }


@app.route('/metrics')
def metrics():
    status = run(["barman", "status", DATABASE_NAME],
                 stdout=PIPE, universal_newlines=True)
    check = run(["barman", "check", DATABASE_NAME],
                 stdout=PIPE, universal_newlines=True)
    if status.returncode == 0 and check.returncode == 0:
        ms = parse_status(status.stdout, check.stdout)
    else:
        ms = {"barman_running": False}
    ms = label_metrics(ms, {"database": DATABASE_NAME})
    return render_metrics(ms)
