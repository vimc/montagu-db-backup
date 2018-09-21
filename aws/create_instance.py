import boto3
from awscli.customizations.emr.constants import EC2

from create_volume import get_or_create_volume
from security_group import create_security_group
from settings import machine_image, instance_type, key_name, availability_zone

ec2 = boto3.resource('ec2')


def create_instance(instance_name):
    group_name = "{}-group".format(instance_name)
    security_group = create_security_group(group_name)

    volume_name = "{}-volume".format(instance_name)
    volume = get_or_create_volume(volume_name)

    print("Requesting new instance...")
    instances = ec2.create_instances(
        DryRun=False,
        ImageId=machine_image,
        InstanceType=instance_type,
        KeyName=key_name,
        MaxCount=1,
        MinCount=1,
        Placement={
            'AvailabilityZone': availability_zone
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'name', 'Value': instance_name}]
            }
        ],
        SecurityGroupIds=[security_group.id],
        UserData=get_startup_script()
    )
    instance = instances[0]

    print("Waiting for instance to be running...")
    instance.wait_until_running()

    print("Attaching EBS volume...")
    # For reasons best known to itself, EC2 maps /dev/sdf to /dev/xvdf, but you
    # can't just attach directly to /dev/xvdf
    instance.attach_volume(
        Device="/dev/sdf",
        VolumeId=volume.id
    )

    return instances[0]


def get_startup_script():
    with open('./bin/startup.sh', 'r') as f:
        code = f.read()
    return code

