#!/usr/bin/env bash
set -e
PASSWORD=$1

PGPASSFILE=/var/lib/barman/.pgpass
cat <<EOF > $PGPASSFILE
*:*:*:barman:$PASSWORD
*:*:*:streaming_barman:$PASSWORD
EOF
chmod 600 $PGPASSFILE
chown barman.barman $PGPASSFILE
