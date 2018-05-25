from io import StringIO
from time import sleep

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from scp import SCPClient

from vault import get_ec2_private_key, get_target_private_key, \
    get_target_host_key


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
        retries = 10
        while not connected:
            try:
                ssh.connect(self.host, username=self.username, pkey=private_key)
                connected = True
            except Exception:
                retries -= 1
                if retries == 0:
                    raise
                sleep(2)
        self.client = ssh

    def wait_for_go_signal(self):
        print("Waiting for go signal...")
        while self._run_remote_cmd("cat go_signal") != "ready":
            sleep(2)

    def run_barman(self):
        with SCPClient(self.client.get_transport()) as scp:
            self._add_known_host(get_target_host_key())
            self._upload_private_key(scp)
            scp.put("bin/run-barman.sh")

        return self._run_remote_cmd("./run-barman.sh")

    def _add_known_host(self, public_key):
        self._run_remote_cmd('echo "{}" >> .ssh/known_hosts '
                             '&& rm public_key'.format(public_key))

    def _upload_private_key(self, scp):
        key_path = ".ssh/id_rsa"
        self._run_remote_cmd("touch {p} && chmod 600 {p}".format(
            p=key_path))
        with StringIO(get_target_private_key()) as key:
            scp.putfo(key, key_path)

    def get_startup_log(self):
        print("Retrieving logs via ssh")
        return self._run_remote_cmd("cat /var/log/cloud-init-output.log")

    def close(self):
        if self.client:
            self.client.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _run_remote_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8').strip()
        err = stderr.read().decode('utf-8').strip()
        if exit_code < 0:
            raise Exception("An error occurred running remote command"
                            "{}: {}".format(cmd, err))
        return out + err

    def _get_key(self):
        return RSAKey.from_private_key(StringIO(get_ec2_private_key()))
