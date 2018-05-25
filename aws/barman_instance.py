from time import sleep

import boto3
from awscli.customizations.emr.constants import EC2
from paramiko import SSHClient

from barman_ssh_client import BarmanSSHClient
from create_instance import create_instance


class BarmanInstance(object):
    def __init__(self, name="montagu-barman", ec2=None):
        self.name = name
        self.ec2 = ec2 or boto3.resource('ec2')
        self._instance: EC2.Instance = None
        self._ssh: SSHClient = None

    @property
    def exists(self):
        return self.instance

    def start(self):
        if self.instance:
            raise Exception("Cannot start another instance: already running")

        self._instance = create_instance()
        print("Id: " + self.id)
        self.wait_for_startup()

    def wait_for_startup(self):
        print("Waiting for instance to be running...")
        self.instance.wait_until_running()
        print("Waiting for DNS...")
        while not self.public_dns_name:
            self.instance.reload()
            sleep(2)
        print("DNS: " + self.public_dns_name)

        with BarmanSSHClient(self.public_dns_name) as ssh:
            ssh.connect()
            ssh.wait_for_go_signal()
            print(ssh.run_barman())

    def stop(self):
        if self.exists:
            print("Requesting termination of {}".format(self.instance.id))
            self.instance.terminate()

    def get_startup_log(self):
        with BarmanSSHClient(self.public_dns_name) as ssh:
            return ssh.get_startup_log()

    @property
    def id(self):
        return self.instance.id

    @property
    def public_dns_name(self):
        return self.instance.public_dns_name

    @property
    def status(self):
        return self.instance.state['Name']

    @property
    def instance(self):
        if not self._instance:
            all = self.ec2.instances.filter(
                Filters=[{
                    'Name': 'tag:name',
                    'Values': [self.name]
                }]
            )
            all = [i for i in all if i.state['Name'] != 'terminated']
            if len(all) > 1:
                raise Exception("More than one ec2 instance running with "
                                "name {}".format(self.name))
            elif len(all) == 1:
                self._instance = all[0]
        return self._instance
