#!/usr/bin/env bash
DEST=/restore
DB=montagu
BACKUPID=$(barman list-backup --minimal $DB | head -n1)

mkdir -p $DEST
# TODO: Assert directory is empty?
barman recover $DB $BACKUPID $DEST
