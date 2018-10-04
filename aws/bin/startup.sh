#!/usr/bin/env bash
EBS=/dev/xvdf

set -ex

# Disable services that come with the image that we don't need
sudo systemctl disable kubelet

# Install required packages
apt-get update
apt-get install -y python3-pip autossh

# We don't actually need this, but it makes it easier to test if
# the port forwarding is working; you can just run:
# `psql -U vimc -d montagu` and see if you get anything
apt get install -y postgresql-client

# Enable normal user to perform docker commands
usermod -aG docker ubuntu

# Format and mount large EBS volume
if [[ $(file -s $EBS) == "$EBS: data" ]]; then
    echo "EBS volume is unformatted. Formatting now"
    mkfs -t ext4 $EBS
fi
fstab_line="$EBS    /mnt/data    ext4    defaults,nofail"
echo $fstab_line | sudo tee --append /etc/fstab
mkdir -p /mnt/data
mount -a

# Enable swap
dd if=/dev/zero of=/var/swap.1 bs=1M count=2048
mkswap /var/swap.1
chmod 600 /var/swap.1
swapon /var/swap.1
fstab_line="/var/swap.1   swap    swap    defaults        0   0"
echo $fstab_line | sudo tee --append /etc/fstab

echo "ready" > /home/ubuntu/go_signal
