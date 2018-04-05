# Montagu DB backup

As the database has grown (from a few 10s of MB up to GB) the dump-and-restore approach we are using is becoming painful.  Downloading from S3 takes quite a while (especially verification with duplicati) and the restore (`pg_restore`) takes a long time to rebuild the indices.

## Deployment

Barman is running on `annex.montagu.dide.ic.ac.uk` as container `montagu-barman`

```
git clone https://github.com/vimc/montagu-db
cd montagu-db/backup
pip3 install -r requirements.txt
```

Then interact with the barman container the `./barman-montagu` command:

```
$ ./montagu-barman --help
Set up barman (Postgres streaming backup) for montagu

Usage:
  barman-montagu setup [options] <host>
  barman-montagu status
  barman-montagu barman [--] [<args>...]
  barman-montagu recover [--wipe-first] [<backup-id>]
  barman-montagu wipe-recover
  barman-montagu destroy

Options:
  --configure-cron          Configure a once-a-minute cron job
  --password-group=<group>  Password group [default: production]
  --image-tag=<tag>         Barman image tag [default: master]
  --pull-image              Pull image before running?
  --no-clean-on-error       Don't clean up container/volumes on error
```

These commands create and pass through to the `barman` process in a long running container that is called `barman-montagu`

To set up barman:

```
./barman-montagu setup --image-tag=i1559 --pull localhost
```

(replace `localhost` with the name or IP address of the host running the montagu postgres container on port 5432 - in a real deployment this is `production.montagu.dide.ic.ac.uk`).

To install the cron job pass `--configure-cron` (which will also require running with `sudo`).  Or to set up cron on an already running barman:

```
sudo ./barman-montagu setup --configure-cron localhost
```

To see a set of status information run

```
./barman-montagu status
```

To interact with barman directly, either do `docker exec barman-montagu barman ...` or use

```

./barman-montagu barman -- --help
```

(the `--` is often optional but disambiguates arguments to `barman-montagu` and for barman).  For example listing files in the most recent backup might look like:

```
./barman-montagu barman list-files montagu latest
```

or getting information about the latest backup:

```
./barman-montagu barman show-backup montagu latest
```

(see [the `barman` docs](http://docs.pgbarman.org/release/2.0) for more commands).

To dump out the latest copy of the database to recover from:

```
./barman-montagu recover --wipe-first
```

You will then need to clone the contents of the `barman_recover` volume into a suitable place to restore from.

To remove all traces of barman (the cron job, the container and the volumes), use:

```
./barman-montagu destroy
```

The `barman-montagu` script does not depend on its location and can be moved to a position within `$PATH`.

## Development notes

This directory creates a new docker image (`vimc/montagu-barman` http://www.pgbarman.org/).

Important notes:

The barman container must be able to reach the montagu-db container over the network.  Depending on how you are deploying this would be either by attaching to the same network (e.g., in testing) or over the network (e.g., in production)

**Three** volumes are used;
1. `barman_data` (at `/var/lib/barman`) is the one that holds the backup - this should itself be backed up
2. `barman_logs` (at `/var/log/barman`) is used to persist logs
3. `barman_restore` (at `/restore`) holds a restore location - ensure that this is empty before restoring into it

Barman needs to know the hostname, port, database name, two user names and two passwords.  Defaults for these are set in [etc/barman.d.in/montagu.json](etc/barman.d.in/montagu.json) but can be overridden by passing environment variables to the container in the form `BARMAN_MONTAGU_<key>` where `<key>` is one of the entries from the json, in uppercase (this can be done either with the `-e` flag or `--env-file` argument (e.g., `BARMAN_MONTAGU_PASS_BACKUP`)

To initialise barman, for now see `demo.sh` and `demo_montagu.sh` - these will be obsoleted by deployment work ([VIMC-1483](https://vimc.myjetbrains.com/youtrack/issue/VIMC-1483)).

Once the barman container is up it just runs an idle loop (which is needed to support the way that barman runs) but runs no interesting processes and does no backup.  To use barman all commands are run via `docker exec barman_container barman ...`, e.g.,

```
docker exec barman_container barman list-backup all
```

The host system should arrange to run `barman cron` via exec regularly (the barman docs suggest once a minute).  It *must* run because otherwise eventually the source database will die because the log shipping has failed.

```
docker exec barman_container barman cron
```

To restore, run:

```
docker exec barman_container restore-last
```

which will set up a postgres filesystem ready for restore within the `barman_restore` volume.  This can then be rsync'd into place.  It may be necessary to use `--ignore-times --checksum` because times are likely to be a real mess here, but I'm not sure that will actually be fast enough either.

## Changes to our current system

This approach is going to preserve a lot more about the system so we will need to be more careful about user creation (basically users will be preserved now).  That will mean moving to a stable user password in the vault but that's not a big deal.  It will also remove a lot of the user management from deploy, and the only password work that should need doing will be to set the passwords for uat to simple values.  We might need to do some delicate tweaks to the migrations.

## Moving things around

If we copy files around, using scp with `-o "Compression no"` can speed things up ~3x (I see for a 2.5GB file 1:36 with compression, 0:34 without). Not sure what rsync will do.

## Restore

1. Stop montagu so that the db stops, but do not remove the data volume
2. Rsync from the restore into the container with appropriate `--delete` flags set: this will hopefully reduce copying around too much
3. Start up montagu!
