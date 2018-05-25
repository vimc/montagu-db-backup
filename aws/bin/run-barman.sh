#!/usr/bin/env bash
set -ex
db_host=aws@montagu.vaccineimpact.org

mkdir barman && cd barman
git clone https://github.com/vimc/montagu-db
cd montagu-db/backup
git checkout i1771  # TODO: return to master
pip3 install -r requirements.txt

# -M -S - Set up SSH in (M)aster mode for connection sharing via the specified
#         (S)ocket file
# -nNT  - Don't read, do anything remotely, or allocate a remote terminal
# -f    - Run in background
# -p    - Connect to SSH server on 10022, as production has a non-standard port
# -L    - Sets up tunnel from local port to remote host & port
ssh -M -S socket \
    -nNT \
    -f \
    -p 10022 \
    -L 5432:localhost:5432 \
    $db_host

# Check the connection is up
ssh -S socket -O check $db_host

trap "ssh -S socket -O exit $db_host" SIGINT SIGTERM

./barman-montagu setup \
    --password-group=fake \
    --pull-image \
    --image-source=vimc \
    --no-clean-on-error \
    localhost   # Forwarded by SSH to the true host
