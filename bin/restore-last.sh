#!/usr/bin/env bash
DEST=/restore
DB=montagu

BACKUPID=$(barman list-backup --minimal $DB | head -n1)

mkdir -p $DEST
# TODO: Assert directory is empty
DEST_UID=$(stat -c '%u' $DEST)
DEST_GID=$(stat -c '%g' $DEST)
chown barman $DEST
barman recover $DB $DEST_UID.$DEST_GID $DEST
chown -R $DEST_UID $DEST
