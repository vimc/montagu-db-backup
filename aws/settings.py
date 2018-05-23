# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
# Cold HDD - Lowest cost HDD volume
volume_type = 'sc1'

# GB, lowest value for sc1
volume_size = 500

# https://aws.amazon.com/ec2/instance-types/
instance_type = 't2.nano'

# Ubuntu 16.04
machine_image = 'ami-587b9e3f'

# Stored in vault at secret/backup/ec2/montagu-barman-keypair
# Created with `aws ec2 create-key-pair --key-name montagu-barman`
key_name = 'montagu-barman'
