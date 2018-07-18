import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')


def get_group_if_exists():
    try:
        groups = list(ec2.security_groups.filter(GroupNames=['montagu-barman']))
        return groups[0]
    except ClientError as e:
        if "NotFound" in str(e):
            return None
        else:
            raise e


def delete_group_if_already_exists():
    group = get_group_if_exists()
    if group:
        group.delete()


def authorize_ingress(group, cidr_ip):
    group.authorize_ingress(
        CidrIp=cidr_ip,
        IpProtocol="tcp",
        FromPort=22,
        ToPort=22
    )


def authorize_egress(group):
    group.authorize_egress(
        IpPermissions=[
            {
                'IpRanges': [
                    {
                        "CidrIp": "129.31.26.29/32",
                        "Description": "montagu.vaccineimpact.org"
                    }
                ],
                'IpProtocol': "tcp",
                'FromPort': 0,
                'ToPort': 9999
            }
        ]
    )


def create_security_group(group_name):
    delete_group_if_already_exists()
    print("Creating new security group...")
    group = ec2.create_security_group(
        Description='Montagu Barman Security Group',
        GroupName=group_name
    )

    allowed_ingress_ranges = [
        "129.31.24.0/23",  # All DIDE workstations
        # "129.31.24.0/24",    # All DIDE servers
    ]

    for cidr in allowed_ingress_ranges:
        authorize_ingress(group, cidr)
    authorize_egress(group)
    return group
