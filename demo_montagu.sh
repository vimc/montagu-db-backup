## Start a montagu


## NOTE: We need to know the ip address of the host where the montagu
## db is running.  This can be done by setting this container to have
## --network=host and using localhost but that will require a
## different configuration when used in anger.  With this approach we
## just set
##
##     MONTAGU_DB_IP=$(host production.montagu.dide.ic.ac.uk)
##
## and the rest of the script remains unchanged.
MONTAGU_DB_IP=$(hostname --ip-address)

## This is the only other bit of configuration needed - it will need
## tweaking if using the 'fake' password group (an if/else here or add
## fake entries into the vault).
MONTAGU_PASSWORD_GROUP=production

## Then the bits that are less interesting to configure:
BARMAN_VOLUME_DATA=barman_data
BARMAN_VOLUME_RESTORE=barman_restore
BARMAN_VOLUME_LOGS=barman_logs
BARMAN_CONTAINER=barman_container
BARMAN_IMAGE=docker.montagu.dide.ic.ac.uk:5000/montagu-barman:master

vault auth -method=github
MONTAGU_PASSWORD_PATH="secret/database/${MONTAGU_PASSWORD_GROUP}/users"
BARMAN_MONTAGU_PASS_BACKUP=$(vault read -field=password \
                                   ${MONTAGU_PASSWORD_PATH}/barman)
BARMAN_MONTAGU_PASS_STREAM=$(vault read -field=password \
                                   ${MONTAGU_PASSWORD_PATH}/streaming_barman)

BARMAN_CONFIG=$(tempfile)
cat > $BARMAN_CONFIG <<EOF
BARMAN_MONTAGU_PASS_BACKUP=$BARMAN_MONTAGU_PASS_BACKUP
BARMAN_MONTAGU_PASS_STREAM=$BARMAN_MONTAGU_PASS_STREAM
EOF

docker volume create $BARMAN_VOLUME_DATA
docker volume create $BARMAN_VOLUME_RESTORE
docker volume create $BARMAN_VOLUME_LOGS

docker run -d --rm \
       --name $BARMAN_CONTAINER \
       -v $BARMAN_VOLUME_DATA:/var/lib/barman \
       -v $BARMAN_VOLUME_LOGS:/var/log/barman \
       -v $BARMAN_VOLUME_RESTORE:/restore \
       --env-file $BARMAN_CONFIG \
       --add-host="db:${MONTAGU_DB_IP}" \
       $BARMAN_IMAGE

rm -f $BARMAN_CONFIG

docker exec $BARMAN_CONTAINER setup-barman

## List and restore:
docker exec $BARMAN_CONTAINER barman list-backup all
docker exec $BARMAN_CONTAINER restore-last

## Run postgres using the restored database
docker run --rm -d \
       --name db_recovered \
       -v $BARMAN_VOLUME_RESTORE:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:master

docker logs --tail 10 db_recovered

docker exec db_recovered psql -U vimc -d montagu -c "\dt"
docker stop db_recovered

docker stop $BARMAN_CONTAINER
docker volume rm $BARMAN_VOLUME_DATA $BARMAN_VOLUME_LOGS $BARMAN_VOLUME_RESTORE
