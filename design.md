## Montagu DB backup - design

Our primary database sits on `production.montagu.dide.ic.ac.uk` on port 5432 (behind the VPN).  It uses streaming replication to stream to two [barman](https://www.pgbarman.org/) instances - one on `annex.montagu.dide.ic.ac.uk`, the other on AWS.

Two concepts are important:

1. a **base backup** is a snapshot of the postgres database at some point in time
2. the **WAL (Write Ahead Log)** which can be replayed from a base backup to the present to restore the current database state

The overall process is described in diagram form [here](https://github.com/vimc/montagu-machine/blob/master/docs/diagrams/Database%20backup.png)

### The restore path

The basic approach (without any real reference to the wrinkles that will appear below) is:

1. On annex, `barman` dumps out a recovery directory (this is a base backup plus the WAL) using `barman recover` into the `montagu_db_volume` volume - this is our "nightly backup".
2. On annex, The nightly backup is then run through a copy of Postgres, using `vimc/montagu-db:latest`, so that the database is fully recovered (`barman revover` dumps the data that Postgres *can* restore, but it takes time for the WAL to be replayed over the base backup) - we're calling this step "replay wal"
3. On annex, `bb8` ships this into the starport using `bb8 backup`, updating the directory on disk `~/starport/barman_to_starport` (this is the only backup target _from_ annex, even though everything else gets sent there).
4. On science (or another machine being restored) `bb8 restore` rsync's the contents of the starport barman into the `montagu_db_volume` container, then starts montagu.

A base backup will take ~2hrs (as of 2020-02-20) and currently requires ~220GB.  If there are significant quantities of WAL logs then it will take longer.  Replaying the WAL can take up to an hour.

Steps 1-3 are done using a cron script that lives in the bb8 repo `schedule-barman-montagu-nightly`.  This cron job can and has stopped without warning in the past - most recently when the Python installation disappeared during an Ubuntu upgrade.

bb8 takes control of the actual process of preparing the recovery volume.  It writes out a cron nightly script that runs the barman `update-nightly` script and then `bb8 backup`

### Base-backups

We run a monthly base backup in the barman container; this is controlled by `schedule.yml` file that runs in the `yacron` instance that powers the barman container.  A new base backup can be made by running

```
barman-montagu barman backup montagu
```

This has implications for cleanup though, as our retention policy guarantees only the last 3 backups will be saved.

On annex, running `barman-montagu status` will print information about the status including the number and timings of backups.

### Off-site backup

Our backup system copies the starport volume into AWS.  There is also a second copy of barman running there.  The AWS setup is described [in the `aws` directory](aws).
