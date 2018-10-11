from app.main import parse_status, metrics

fake_barman_status = """
    Active: True
    Disabled: False
    PostgreSQL version: 10.3
    Cluster state: in production
    pgespresso extension: Not available
    Current data size: 110.2 GiB
    PostgreSQL Data directory: /pgdata
    Current WAL segment: 00000001000000BC0000006A
    Retention policies: enforced (mode: auto, retention: RECOVERY WINDOW OF 3 MONTHS, WAL retention: MAIN)
    No. of available backups: 0
    First available backup: None
    Last available backup: None
    Minimum redundancy requirements: satisfied (3/0)
"""


fake_barman_check = """
    PostgreSQL: OK
    is_superuser: OK
    PostgreSQL streaming: OK
    wal_level: OK
    replication slot: OK
    directories: OK
    retention policy settings: OK
    backup maximum age: OK (no last_backup_maximum_age provided)
    compression settings: OK
    failed backups: OK (there are 0 failed backups)
    minimum redundancy requirements: OK (have 3 backups, expected at least 0)
    pg_basebackup: OK
    pg_basebackup compatible: OK
    pg_basebackup supports tablespaces mapping: OK
    pg_receivexlog: OK
    pg_receivexlog compatible: OK
    receive-wal running: OK
    archiver errors: OK
"""


def test_endpoint_handles_arbitrary_error(monkeypatch):
    monkeypatch.setenv('BARMAN_DATABASE_NAME', 'test')
    # the call to barman status and barman check will fail in this testing context
    # causing an error
    response = metrics()
    assert response.status_code == 200

    response_text = response.get_data(as_text=True)
    assert response_text == "barman_responding 0\n"


def test_parse_status_handles_no_available_backup():

    # setup
    result = parse_status(fake_barman_status, fake_barman_check)
    assert result == {
        "barman_running": True,
        "barman_ok": True,
        "barman_pg_version": "10.3",
        "barman_available_backups": "0",
        "barman_time_since_last_backup_seconds": None,
        "barman_time_since_last_backup_minutes": None,
        "barman_time_since_last_backup_hours": None,
        "barman_time_since_last_backup_days": None
    }

