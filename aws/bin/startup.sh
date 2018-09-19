#!/usr/bin/env bash
EBS=/dev/xvdf

set -ex
apt-get update
apt-get install -y python3-pip autossh

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

echo "ready" > /home/ubuntu/go_signal
