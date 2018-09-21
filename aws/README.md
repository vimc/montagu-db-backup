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
