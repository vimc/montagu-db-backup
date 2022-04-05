# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
# Cold HDD - Lowest cost HDD volume
volume_type = 'sc1'

# GB, 500 is the lowest value for sc1
volume_size = 1500

# https://aws.amazon.com/ec2/instance-types/
instance_type = 't2.nano'

# Ubuntu 16.04
machine_image = 'ami-587b9e3f'

# Stored in vault at secret/vimc/backup/ec2/montagu-barman-keypair
# Created with `aws ec2 create-key-pair --key-name montagu-barman`
key_name = 'montagu-barman'

# This is an EBS key managed by Amazon KMS, it's not the same as the
# key referred to by settings.key_name
kms_key_id = 'cf0192d9-10be-4561-8d31-fbe32c11a048'

# Doesn't matter too much, so long as it's in Europe and it matches for both
# volume and instance
availability_zone = "eu-west-2a"
