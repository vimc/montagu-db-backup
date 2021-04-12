#!/usr/bin/env bash
set -ex

WORKDIR=$(mktemp -d)

function finish {
    rm -rf $WORKDIR
}
trap finish EXIT

git clone https://github.com/vimc/machine-metrics.git $WORKDIR
git -C $WORKDIR checkout vimc-4690
(cd "${WORKDIR}" && sudo -H ./install)
