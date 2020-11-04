# Barman on AWS
The first time you use these scripts on your machine run:

1. `sudo -H ./prepare`
2. `aws configure`. You will be promoted to enter your AWS credentials and a region.
    To create a new key see [the wiki](https://github.com/vimc/vimc-wiki/wiki/AWS-things)
    The region should be `eu-west-2`.
3. Make sure you have the submodule: `git submodule init && git submodule update` 

Then run `./aws-barman` to see all options, or `./aws-barman start` to start a
new instance.

Note `aws-barman stop` will destroy the existing EC2 instance.

To interact directly with barman in the aws machine:

* `./aws-barman ssh`
* `cd barman/montagu-db-backup`
* `./barman-montagu status` (etc)

Are the metrics running?

* `./aws-barman status`
* go to the Instance DNS (e.g., ec2-35-178-211-45.eu-west-2.compute.amazonaws.com), port 5000, at the `/metrics` endpoint

## Rebooting EC2 instance
It may be that we never want to do this, and this it's always better to
destroy and recreate the instance, but here's the steps I followed to do
this on 2018-10-01. I'm more documenting this for when Rich has time to
generally make it easier to re-setup / restart barman instances in
general.

1. Reboot instance using AWS console
2. SSH in
3. Restart stopped container: `docker start barman-montagu`
4. Restart autossh:
   ```
   autossh -M 20000 -nNT -f -p 10022 -L 5432:montagu.vaccineimpact.org:5432 aws@montagu.vaccineimpact.org
   ```
5. Restart the cron job:
   ```
   docker exec barman-montagu setup-barman
   ```

## Deleting failed backups

Get onto the aws machine with:

```
./aws-barman ssh
```

```
cd barman/montagu-db-backup
```

Confirm the problem

```
./barman-montagu barman -- check montagu
```

where you may see

```
        failed backups: FAILED (there are 1 failed backups)
```


```
./barman-montagu barman -- list-backup montagu
```

which will show something like

```
montagu 20201101T000001 - Mon Nov  2 05:49:25 2020 - Size: 345.4 GiB - WAL Size: 0 B
montagu 20201001T010001 - FAILED
montagu 20200901T010001 - Wed Sep  2 03:50:09 2020 - Size: 324.4 GiB - WAL Size: 31.7 GiB
montagu 20200804T110556 - Wed Aug  5 15:46:30 2020 - Size: 325.9 GiB - WAL Size: 2.0 GiB
montagu 20200701T010001 - Wed Jul  1 01:14:43 2020 - Size: 301.6 GiB - WAL Size: 32.2 GiB
```

Delete the offending backup

```
./barman-montagu barman -- delete montagu 20201001T010001
```

Verify:

```
./barman-montagu barman -- check montagu
```
