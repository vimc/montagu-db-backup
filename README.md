# Montagu DB backup

As the database has grown (from a few 10s of MB up to GB) the dump-and-restore
approach we are using is becoming painful.  Downloading from S3 takes quite a
while (especially verification with duplicati) and the restore (`pg_restore`)
takes a long time to rebuild the indices.

## Design

See [`design.md`](design.md) for a description of the system with less archaelogical content.

## Deployment

Barman is running on `annex.montagu.dide.ic.ac.uk` as container `montagu-barman`

```
git clone https://github.com/vimc/montagu-db-backup
cd montagu-db-backup
pip3 install -r requirements.txt
```

Then install the command with

```
sudo ./install
```

which sets up a `barman-montagu` command that can be used from anywhere on the
computer that refers to the configuration in *this* directory (you can also use
`./barman-montagu` and avoid installing).

Then you can interact with the barman container the `barman-montagu` command:

```
$ barman-montagu --help
Set up and use barman (Postgres streaming backup) for montagu

Usage:
  barman-montagu setup [options] --slot=<slot> <host>
  barman-montagu status
  barman-montagu barman [--] [<args>...]
  barman-montagu recover [--wipe-first] [<backup-id>]
  barman-montagu update-nightly
  barman-montagu wipe-recover
  barman-montagu destroy

Options:
  --password-group=<group>  Password group [default: production]
  --image-tag=<tag>         Barman image tag [default: master]
  --image-source=<repo>     The Docker registry to pull from [default:
  docker.montagu.dide.ic.ac.uk:5000]
  --pull-image              Pull image before running?
  --no-clean-on-error       Don't clean up container/volumes on error
  --slot=<slot>             Replication slot to use on the db

```

These commands create and pass through to the `barman` process in a long running
container that is called `barman-montagu`

To set up barman:

```
barman-montagu setup --pull-image --slot barman production.montagu.dide.ic.ac.uk
./start-metrics.sh       # Exposes Prometheus metrics on port 5000
```

Or, for local testing you would want:

```
barman-montagu setup --pull-image --slot barman localhost
```

Or, for testing a locally built barman image, something like:

```
docker build --tag montagu-barman:test .
./barman-montagu setup \
    --slot=barman \
    --image-source= \
    --image-tag=test \
    --password-group=production \
    localhost
```

Currently the port 5432 is assumed.

## Monitoring barman
Barman serves up OpenTSDB formatted (i.e. Prometheus-compatible) metrics
at port 5000 on the host machine it is run on, using a Flask app that we
wrote. It should give you output in roughly this format:

```
barman_running{database="montagu"} 1
barman_ok{database="montagu"} 1
barman_pg_version{database="montagu"} 10.3
barman_available_backups{database="montagu"} 1
barman_time_since_last_backup_seconds{database="montagu"} 54.008972
barman_time_since_last_backup_minutes{database="montagu"} 0.9001495333333334
barman_time_since_last_backup_hours{database="montagu"} 0.015002492222222222
barman_time_since_last_backup_days{database="montagu"} 0.0006251038425925926
```

Prometheus adds two labels to every metric: instance_name and job. Plus we
have a manual label here: database. So if we have two barman instances
tracking the same db (as we do: production and AWS) they will differ by
instance_name. And if they are tracking different databases they will also
differ by database.

### Tests
To test the metrics Flask app, run
```
cd ./backup/metrics
sudo -H  pip3 install -r ./bin/requirements.txt
sudo -H  pip3 install -r ./bin/requirements-dev.txt
pytest
```

On Teamcity we run these tests inside a docker container using `./backup/metrics/scripts/teamcity.sh`

## Interacting with barman
To see a set of status information run

```
barman-montagu status
```

To interact with barman directly, either do `docker exec barman-montagu barman ...` or use

```

barman-montagu barman -- --help
```

(the `--` is often optional but disambiguates arguments to `barman-montagu` and
for barman).  For example listing files in the most recent backup might look
like:

```
barman-montagu barman list-files montagu latest
```

or getting information about the latest backup:

```
barman-montagu barman show-backup montagu latest
```

(see [the `barman` docs](http://docs.pgbarman.org/release/2.0) for more commands).

To dump out the latest copy of the database to recover from:

```
barman-montagu recover --wipe-first
```

You will then need to clone the contents of the `barman_recover` volume into a
suitable place for the Postgres server to read from.

Every night a snapshot of the database can be written out to the
`montagu_db_volume` volume, by running

```
barman-montagu update-nightly
```

This should be arranged to run on your host machine.

For a manual dump, prefer the `barman-montagu recover` which writes to the
`barman_recover` volume.

To remove all traces of barman (the container and the volumes), use:

```
barman-montagu destroy
```

The `barman-montagu` script does not depend on its location and can be moved to
a position within `$PATH`.

## About the connections

Each of the barman instances will use up to two connections - one for the streaming wal and the other for a base backup.

You can see what is connected by logging onto production with `psql` and running

```
select usename, application_name, client_addr, backend_start, state_change
 from pg_stat_activity where application_name like '%barman%';
```

which will look like this:

```
     usename      |    application_name     | client_addr  |         backend_start         |         state_change
------------------+-------------------------+--------------+-------------------------------+-------------------------------
 streaming_barman | barman_streaming_backup | 129.31.26.49 | 2018-09-21 13:33:31.587082+00 | 2018-09-21 13:33:31.590201+00
 streaming_barman | barman_streaming_backup | 129.31.26.29 | 2018-09-21 13:29:47.57013+00  | 2018-09-21 13:29:47.586758+00
 streaming_barman | barman_receive_wal      | 129.31.26.29 | 2018-09-21 13:28:02.92548+00  | 2018-09-21 13:28:02.946786+00
 streaming_barman | barman_receive_wal      | 129.31.26.49 | 2018-09-21 12:50:02.129403+00 | 2018-09-21 12:50:02.132366+00
```

The IP address for the aws machine will show up as production (129.31.26.29) and we think that's because of the ssh tunnel.

## Updating the barman container

We want to deploy a new version of barman to run, but keep all the data intact. This is the proceedure

* Log in to `annex.montagu` and go to `montagu-db-backup`
* Update the repo as required
* `docker stop barman-montagu`
* `docker rm barman-montagu`
* `./barman-montagu setup --pull-image --slot barman production.montagu.dide.ic.ac.uk`

## Development notes

This directory creates a new docker image (`vimc/montagu-barman` http://www.pgbarman.org/).

Important notes:

The barman container must be able to reach the montagu-db container over the
network. Depending on how you are deploying this would be either by attaching
to the same network (e.g., in testing) or over the network (e.g., in production)

**Four** volumes are used;
1. `barman_data` (at `/var/lib/barman`) is the one that holds the backup - this should itself be backed up
2. `barman_logs` (at `/var/log/barman`) is used to persist logs
3. `barman_recover` (at `/recover`) holds a manual recovery location - ensure that this is empty before restoring into it
4. `montagu_db_volume` (at `/nightly`) holds a periodic recovery

Barman needs to know the hostname, port, replication slot, database name, two
user names and two passwords. Defaults for these are set in
[etc/barman.d.in/montagu.json](etc/barman.d.in/montagu.json) but can be
overridden by passing environment variables to the container in the form
`BARMAN_MONTAGU_<key>` where `<key>` is one of the entries from the json, in
uppercase (this can be done either with the `-e` flag or `--env-file` argument
(e.g., `BARMAN_MONTAGU_PASS_BACKUP`).

There is no default for the replication slot, as connecting two barman instances
accidentally to the same replication slot can cause data to be missed from the
backup. For the instance running on the annex we use a slot called `barman`. So
you can set this with `-e BARMAN_MONTAGU_SLOT_NAME=barman`.

To initialise barman, for now see `demo.sh` and `demo_montagu.sh` - these will
be obsoleted by deployment work
([VIMC-1483](https://vimc.myjetbrains.com/youtrack/issue/VIMC-1483)).

Once the barman container is up it just runs an idle loop (which is needed to
support the way that barman runs) but runs no interesting processes and does no
backup.  To use barman all commands are run via `docker exec barman_container
barman ...`, e.g.,

```
docker exec barman_container barman list-backup all
```

To restore, run:

```
docker exec barman_container recover-last
```

which will set up a postgres filesystem ready for recovery within the
`barman_recover` volume.  This can then be rsync'd into place.  It may be
necessary to use `--ignore-times --checksum` because times are likely to be a
real mess here, but I'm not sure that will actually be fast enough either.

## Changes to our current system

This approach is going to preserve a lot more about the system so we will need
to be more careful about user creation (basically users will be preserved now).
That will mean moving to a stable user password in the vault but that's not a
big deal.  It will also remove a lot of the user management from deploy, and the
only password work that should need doing will be to set the passwords for uat
to simple values.  We might need to do some delicate tweaks to the migrations.

## Moving things around

If we copy files around, using scp with `-o "Compression no"` can speed things
up ~3x (I see for a 2.5GB file 1:36 with compression, 0:34 without). Not sure
what rsync will do.

## Restore

1. Stop montagu so that the db stops, but do not remove the data volume
2. Rsync from the restore into the container with appropriate `--delete` flags set: this will hopefully reduce copying around too much
3. Start up montagu!

## Testing

Copy `testing/montagu-deploy.json` into your `montagu/src` directory - this
creates a minimal montagu deployment that supports streaming replication.

Run:

```
barman-montagu setup --pull-image localhost
```

(you may want to specify `--image-tag` too to run the branch you're working on).
