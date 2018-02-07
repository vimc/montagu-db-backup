## As for demo.sh but assuming that we have montagu running via
## deploy.  This will have created
##
## - a network 'montagu_default'
## - a container 'montagu_db_1'
## - postgres on the network has hostname 'db'
##
## We will assume all of that here:
MONTAGU_NETWORK=montagu_default
MONTAGU_DB_CONTAINER=montagu_db_1
MONTAGU_DB_NAME=db

## These will need configuring through the deploy script too
BARMAN_VOLUME_DATA=barman_data
BARMAN_VOLUME_RESTORE=barman_restore
BARMAN_VOLUME_LOGS=barman_logs
BARMAN_CONTAINER=barman_container
BARMAN_IMAGE=docker.montagu.dide.ic.ac.uk:5000/montagu-barman:i1333

## Prep in the postgres container - this shoulld happen during deploy:
docker exec $MONTAGU_DB_CONTAINER enable-replication.sh changeme changeme

docker volume create $BARMAN_VOLUME_DATA
docker volume create $BARMAN_VOLUME_RESTORE
docker volume create $BARMAN_VOLUME_LOGS

## NOTE: this only works because:
## * postgres db is 'db'
## * passwords are appropriately set
docker run -d --rm \
       --name $BARMAN_CONTAINER \
       --network $MONTAGU_NETWORK \
       -v $BARMAN_VOLUME_DATA:/var/lib/barman \
       -v $BARMAN_VOLUME_LOGS:/var/log/barman \
       -v $BARMAN_VOLUME_RESTORE:/restore \
       $BARMAN_IMAGE
docker exec $BARMAN_CONTAINER setup-barman

## List and restore:
docker exec $BARMAN_CONTAINER barman list-backup all
docker exec $BARMAN_CONTAINER restore-last

## Run postgres using the restored database
docker run --rm -d \
       --name db_recovered \
       -v $BARMAN_VOLUME_RESTORE:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:i1333

docker logs --tail 10 db_recovered

docker exec -it db_recovered psql -U vimc -d montagu -c "\dt"
docker stop db_recovered
