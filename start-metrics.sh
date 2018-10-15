#!/usr/bin/env bash
set -ex
CONFIG_PATH=$(realpath cached-metrics-config.json)
./cached-metrics/scripts/run $CONFIG_PATH --public
