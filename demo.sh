#!/usr/bin/env bash
set -ex

## Until it is set up in teamcity (which requires merge to master)
## build the container with:
HERE=$(dirname $0)
(cd $HERE; ./teamcity-build.sh)

function assert_volume_missing() {
    NAME=$1
    if docker volume inspect $NAME > /dev/null 2>&1; then
        echo "Volume $NAME already exists - remove with:"
        echo "    docker volume rm $NAME"
        exit 1
    fi
}

assert_volume_missing db_data
assert_volume_missing barman_data
assert_volume_missing barman_restore

docker volume create db_data
docker volume create barman_data
docker volume create barman_restore
docker network create pg_nw || true

function cleanup {
    echo "Cleaning up"
    set +e
    docker stop db barman_container db_recovered
    docker volume rm db_data barman_data barman_restore
    docker network rm pg_nw
}
trap cleanup EXIT

docker run --rm -d \
       --name db \
       --network pg_nw \
       -p 5435:5432 \
       -v db_data:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:i1333
docker exec db montagu-wait.sh

## This is something that needs to be done at the right place in each
## deployment.
docker exec db create-users.sh

## This will fit pretty happily into the general deployment approach
## that we have.  This, in addition to setting barman's password, also
## creates the replication slot on the server if it is not there
## already.
docker exec db enable-replication.sh changeme changeme

## Or, put at least one transaction worth of data in:
docker run --rm --network=pg_nw \
       docker.montagu.dide.ic.ac.uk:5000/montagu-migrate:i1333


## Get barman up
docker run -d --rm \
       --name barman_container \
       --network pg_nw \
       -v barman_data:/var/lib/barman \
       -v barman_restore:/restore \
       docker.montagu.dide.ic.ac.uk:5000/montagu-barman:i1333

docker exec barman_container setup-barman

# If running noninteractively it seems to take barman a little time to
# get all the wal files in place.  This was not an issue when I ran
# with the full montagu restore so might be an issue with very empty
# dbs?
sleep 60

docker exec barman_container barman list-backup all
docker exec barman_container restore-last

## Then try and use the instance:
docker run --rm -d \
       --name db_recovered \
       -v barman_restore:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:i1333
docker exec db_recovered montagu-wait.sh
docker exec -it db_recovered \
       psql -U vimc -d montagu -c \
       "\dt"

## Again, but without the server running:
docker stop db
docker stop db_recovered
docker exec barman_container wipe-restore
docker stop barman_container

docker run --rm \
       --entrypoint restore-last-no-server \
       -v barman_data:/var/lib/barman \
       -v barman_restore:/restore \
       docker.montagu.dide.ic.ac.uk:5000/montagu-barman:i1333

docker run --rm -d \
       --name db_recovered \
       -v barman_restore:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:i1333
docker exec db_recovered montagu-wait.sh
docker exec -it db_recovered \
       psql -U vimc -d montagu -c \
       "\dt"
docker stop db_recovered
