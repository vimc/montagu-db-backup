import socket
from io import StringIO
from time import sleep

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from scp import SCPClient

from vault import vault_client, get_private_key


class BarmanSSHClient(object):
    def __init__(self, host: str):
        self.host = host
        self.username = "ubuntu"
        self.client: SSHClient = None

    def connect(self):
        if self.client:
            raise Exception("Already connected")

        print("Establishing SSH connection to {}".format(self.host))
        ssh = SSHClient()
        # Connect to hosts that don't appear in known_hosts
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        private_key = self._get_key()
        connected = False
        while not connected:
            try:
                ssh.connect(self.host, username=self.username, pkey=private_key)
                connected = True
            except socket.gaierror:
                sleep(2)
        self.client = ssh

    def wait_for_go_signal(self):
        print("Waiting for go signal...")
        while self._run_remote_cmd("cat go_signal || true") != "ready":
            sleep(2)

    def run_barman(self):
        with SCPClient(self.client.get_transport()) as scp:
            scp.put("bin/run-barman.sh")
        return self._run_remote_cmd("./run-barman.sh")

    def get_startup_log(self):
        print("Retrieving logs via ssh")
        return self._run_remote_cmd("cat /var/log/cloud-init-output.log")

    def close(self):
        if self.client:
            self.client.close()

    def _run_remote_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command("cat ~/go_signal")
        return stdout.read().decode('utf-8').strip() == "ready"

    def _get_key(self):
        with StringIO() as io:
            io.write(get_private_key())
            return RSAKey.from_private_key_file(io)
