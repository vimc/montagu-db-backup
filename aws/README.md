# Barman on AWS
First time only, run:

1. `sudo -H ./prepare`
2. `aws configure`

The region should be `eu-west-2`.  To create a new key see [the wiki](https://github.com/vimc/vimc-wiki/wiki/AWS-things)

Then run `./aws-barman` to see all options, or `./aws-barman start` to start a
new instance.

To interact directly with barman in the aws machine:

* `./aws-barman ssh`
* `cd barman/montagu-db/backup`
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
   autossh -M 20000 -nNT -f -p 10022 -L 5432:$db_host:5432 aws@montagu.vaccineimpact.org
   ```
5. Restart the cron job:
   ```
   docker exec barman-montagu setup-barman --no-initial-backup
   ```


