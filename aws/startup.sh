#!/usr/bin/env bash
set -ex

mkdir /barman && cd /barman
git clone https://github.com/vimc/montagu-db
cd montagu-db/backup
pip3 install -r requirements.txt

./barman-montagu setup \
    --configure-cron \
    --password-group=fake \
    --pull-image \
    --no-clean-on-error \
    montagu.vaccineimpact.org
