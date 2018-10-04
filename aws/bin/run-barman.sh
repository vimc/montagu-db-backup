#!/usr/bin/env bash
set -ex

db_host="montagu.vaccineimpact.org"
user_and_host="aws@$db_host"

source ./db_passwords && rm ./db_passwords

mkdir barman && cd barman
git clone https://github.com/vimc/montagu-db
cd montagu-db/backup
git checkout master
pip3 install -r requirements.txt

# http://www.harding.motd.ca/autossh/README.txt
# autossh monitors the SSH connection and restarts it if it drops
# autossh options
# -M    - A free port to use for autossh to monitor its own status
# -f    - Run in background

# options passed through to each SSH connection
# -nNT  - Don't read, do anything remotely, or allocate a remote terminal
# -p    - Connect to SSH server on 10022, as production has a non-standard port
# -L    - Sets up tunnel from local port to remote host & port
echo AUTOSSH_LOGFILE="$HOME/autossh.log" >> ~/.profile
source ~/.profile
autossh -M 20000 \
    -nNT \
    -f \
    -p 10022 \
    -L 5432:$db_host:5432 \
    $user_and_host

# -u makes Python not buffer stdout, so we can monitor remotely
# localhost is forwarded by SSH to the true host
# For unknown reasons, this line refuses to break over multiple lines
python3 -u ./barman-montagu setup --pull-image --image-source=vimc --no-clean-on-error --no-initial-backup --slot=barman_aws --volume_data=/mnt/data/barman_data --volume_logs=/mnt/data/barman_logs --volume_recover=/mnt/data/barman_recover localhost

echo "------------------------------------------------------"
echo "you maybe want to run a base backup now"
echo
echo "to do so"
echo
echo "./aws-barman ssh"
echo "cd barman/montagu-db/backup"
echo "screen"
echo "./barman-montagu barman backup montagu"
