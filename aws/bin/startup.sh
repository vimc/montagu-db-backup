#!/usr/bin/env bash
set -ex
apt-get update
apt-get install -y python3-pip
echo "ready" > /home/ubuntu/go_signal
