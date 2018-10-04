import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')


def get_group_if_exists(group_name):
    try:
        groups = list(ec2.security_groups.filter(GroupNames=[group_name]))
        return groups[0]
    except ClientError as e:
        if "NotFound" in str(e):
            return None
        else:
            raise e


def delete_group_if_already_exists(group_name):
    group = get_group_if_exists(group_name)
    if group:
        print("Deleting existing security group...")
        group.delete()


def authorize_ingress(group, cidr_ip, port):
    print("Opening port {port} to {range}".format(port=port, range=cidr_ip))
    group.authorize_ingress(
        CidrIp=cidr_ip,
        IpProtocol="tcp",
        FromPort=port,
        ToPort=port
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
    delete_group_if_already_exists(group_name)
    print("Creating new security group...")
    group = ec2.create_security_group(
        Description='Montagu Barman Security Group',
        GroupName=group_name
    )

    allowed_ingress_ranges = [
        # http://jodies.de/ipcalc?host=129.31.24.0&mask1=23&mask2=
        # All DIDE workstations: 129.31.24.1 ... 129.31.25.254
        # /24 is DIDE *servers* covering only up to 129.31.24.254
        # (larger mask size, fewer addresses unmasked)
        "129.31.24.0/23",
        # Support
        "129.31.26.30/32"
    ]

    for cidr in allowed_ingress_ranges:
        authorize_ingress(group, cidr, port=22)
        authorize_ingress(group, cidr, port=5000)
        authorize_ingress(group, cidr, port=9100)

    authorize_egress(group)
    return group
