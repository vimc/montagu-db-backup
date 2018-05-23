import boto3

from security_group import get_or_create_security_group
from settings import machine_image, instance_type, key_name, volume_size, \
    volume_type

ec2 = boto3.resource('ec2')


def create_instance():
    security_group = get_or_create_security_group()

    block_device = {
        'DeviceName': '/dev/sdb',
        'VirtualName': 'ephemeral0',
        'Ebs': {
            'Encrypted': True,
            'DeleteOnTermination': True,
            'KmsKeyId': 'cf0192d9-10be-4561-8d31-fbe32c11a048',
            'VolumeSize': volume_size,
            'VolumeType': volume_type
        }
    }

    print("Requesting new instance...")
    instances = ec2.create_instances(
        DryRun=False,
        BlockDeviceMappings=[block_device],
        ImageId=machine_image,
        InstanceType=instance_type,
        KeyName=key_name,
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'name', 'Value': 'montagu-barman'}]
            }
        ],
        SecurityGroupIds=[security_group.id],
        UserData=get_startup_script()
    )
    return instances[0]


def get_startup_script():
    with open('./startup.sh', 'r') as f:
        code = f.read()
    return code

