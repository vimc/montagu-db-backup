#!/usr/bin/env bash
set -ex

./barman-montagu setup --image-tag=i1559 --pull localhost
./barman-montagu recover

docker run --rm -d \
       --name db_recovered \
       -v barman_recover:/pgdata \
       docker.montagu.dide.ic.ac.uk:5000/montagu-db:master
docker exec db_recovered montagu-wait.sh
docker logs --tail 10 db_recovered
docker exec db_recovered psql -U vimc -d montagu -c "\dt"
docker stop db_recovered

./barman-montagu destroy
