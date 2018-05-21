#!/usr/bin/env bash
set -ex

apt-get update
apt-get install -y python3-pip

mkdir /barman && cd /barman
git clone https://github.com/vimc/montagu-db
cd montagu-db/backup
pip3 install -r requirements.txt

./barman-montagu setup \
    --password-group=fake \
    --pull-image \
    --no-clean-on-error \
    montagu.vaccineimpact.org
