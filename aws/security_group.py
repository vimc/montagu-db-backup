import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')


def catch_client_error(try_block, catch, on_catch=None):
    def decorated():
        try:
            try_block()
        except ClientError as e:
            if catch in str(e):
                if on_catch:
                    on_catch()
            else:
                raise e


def get_group():
    groups = list(ec2.security_groups.filter(GroupNames=['montagu-barman']))
    return groups[0]


def create_group():
    print("Creating new security group...")
    return ec2.create_security_group(
        Description='Montagu Barman Security Group',
        GroupName="montagu-barman"
    )


def authorize_ingress(group):
    group.authorize_ingress(
        CidrIp="129.31.24.0/23",  # All DIDE workstations
        # CidrIp="129.31.24.0/24",  # All DIDE servers
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


def get_or_create_security_group():
    group = catch_client_error(get_group,
                               catch="NotFound",
                               on_catch=create_group)
    catch_client_error(lambda: authorize_ingress(group),
                       catch="InvalidPermission.Duplicate")
    catch_client_error(lambda: authorize_egress(group),
                       catch="InvalidPermission.Duplicate")
    return group
