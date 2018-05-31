from io import StringIO
from time import sleep

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from scp import SCPClient

from vault import VaultClient


class BarmanSSHClient(object):
    def __init__(self, host: str, vault: VaultClient):
        self.host = host
        self.username = "ubuntu"
        self.client: SSHClient = None
        self.vault = vault

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
        # The startup script we pass to AWS in create_instance, which resides at
        # bin/startup.sh locally, writes to a file at a known location. So if
        # we monitor this file we know when the instance has finished its
        # startup.
        print("Waiting for go signal...")
        while self._run_remote_cmd("cat go_signal") != "ready":
            sleep(2)

    def run_barman(self):
        print("Copying files needed to run barman...")
        with SCPClient(self.client.get_transport()) as scp:
            self._add_known_host(self.vault.target_host_key)
            self._upload_private_key(scp)
            self._upload_db_passwords(scp)
            scp.put("bin/run-barman.sh")

        print("Running barman...")
        self._run_long_remote_cmd("./run-barman.sh")

    def _add_known_host(self, public_key):
        self._run_remote_cmd('echo "{}" >> .ssh/known_hosts '.format(
            public_key))

    def _upload_private_key(self, scp):
        key_path = ".ssh/id_rsa"
        self._run_remote_cmd("touch {p} && chmod 600 {p}".format(
            p=key_path))
        with StringIO(self.vault.target_private_key) as key:
            scp.putfo(key, key_path)

    def _upload_db_passwords(self, scp):
        print("Adding db passwords...")
        passwords = """
export MONTAGU_DB_PASSWORD_barman={barman}
export MONTAGU_DB_PASSWORD_streaming_barman={streaming_barman}
""".format(**self.vault.get_barman_passwords())
        with StringIO(passwords) as token_fo:
            scp.putfo(token_fo, "db_passwords")

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

    # Heavily based off https://stackoverflow.com/questions/23504126/do-you-have-to-check-exit-status-ready-if-you-are-going-to-check-recv-ready/32758464#32758464
    def _run_long_remote_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        channel = stdout.channel  # shared channel for stdout/stderr/stdin
        stdin.close()
        channel.shutdown_write()

        def print_line(data):
            print(data.decode('utf-8'), end='')

        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
            got_chunk = False
            sleep(0.25)
            if channel.recv_ready():
                print_line(channel.recv(len(channel.in_buffer)))
                got_chunk = True
            if channel.recv_stderr_ready():
                print_line(channel.recv_stderr(len(channel.in_stderr_buffer)))
                got_chunk = True

            if not got_chunk \
                    and stdout.channel.exit_status_ready() \
                    and not stderr.channel.recv_stderr_ready() \
                    and not stdout.channel.recv_ready():
                stdout.channel.shutdown_read()
                stdout.channel.close()
                break

        if channel.recv_exit_status() != 0:
            raise Exception("An error occurred running the remote command")

    def _get_key(self):
        return RSAKey.from_private_key(StringIO(self.vault.ec2_private_key))
