#!/usr/bin/env bash
set -ex
apt-get update
apt-get install -y python3-pip

usermod -aG docker ubuntu

echo "ready" > /home/ubuntu/go_signal
