#!/usr/bin/env bash
set -ex

git clone https://github.com/vimc/machine-metrics.git
cd machine-metrics
sudo -H ./install.sh
