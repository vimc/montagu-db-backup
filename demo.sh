# docker stop pg_server barman pg_restore
# docker volume rm pg_server_data barman_data barman_restore barman_etc
# docker network rm pg_nw

./teamcity-build.sh

docker network create pg_nw
docker volume create pg_server_data
docker volume create barman_data
docker volume create barman_restore

docker run --rm -d \
       --name pg_server \
       --network pg_nw \
       -p 5435:5432 \
       -v pg_server_data:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:i1333
docker exec pg_server montagu-wait.sh

## This will fit pretty happily into the general deployment approach
## that we have.  This, in addition to setting barman's password, also
## creates the replication slot on the server if it is not there
## already.
docker exec pg_server set-barman-password.sh changeme

## Restore the db - this takes *ages* unfortunately, particularly on
## docker cp db.dump pg_server:/db.dump
## docker exec pg_server restore-dump.sh /db.dump
## docker exec rm /db.dump

## Or, put at least one transaction worth of data in:
docker exec -it pg_server psql -w -U vimc -d montagu -c 'CREATE TABLE foo (bar INTEGER)'
docker exec -it pg_server psql -w -U vimc -d montagu -c 'INSERT INTO foo VALUES (1);'

docker run -d --rm \
       --name barman_container \
       --network pg_nw \
       -v barman_data:/var/lib/barman \
       -v barman_restore:/restore \
       docker.montagu.dide.ic.ac.uk:5000/montagu-barman:i1333

docker exec barman_container setup-barman
docker exec barman_container barman list-backup all
docker exec barman_container restore-last

## Then try and use the instance:
docker run --rm -d \
       --name pg_server_recovered \
       -v barman_restore:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:i1333
docker exec pg_server_recovered montagu-wait.sh
docker exec -it pg_server_recovered \
       psql -U vimc -d montagu -c \
       "\dt"
