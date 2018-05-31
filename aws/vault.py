import os

import hvac

DEFAULT_VAULT_ADDR = "https://support.montagu.dide.ic.ac.uk:8200"


def save_securely(path, data):
    with open(path, 'a'):  # Create file if does not exist
        pass
    os.chmod(path, 0o600)
    with open(path, 'w') as f:
        f.write(data)


class VaultClient(object):
    def __init__(self):
        vault_url = os.environ.get("VAULT_ADDR", DEFAULT_VAULT_ADDR)
        vault_token = os.environ.get("VAULT_AUTH_GITHUB_TOKEN")
        if not vault_token:
            print("Please paste your vault GitHub access token: ", end="")
            vault_token = input().strip()
        self.client = hvac.Client(url=vault_url)
        print("Authenticating to vault with GitHub")
        self.client.auth_github(vault_token)

    def _read_secret(self, path, field='value'):
        secret = self.client.read(path)
        return secret['data'][field]

    @property
    def ec2_private_key(self):
        """Returns the key that we use to SSH into the ec2 instance.
        The instance is set up to trust this key by the KeyName parameter in
        create_instance. Amazon holds the public key and is able to inject it
        into authorized_keys on each new instance."""
        return self._read_secret('secret/backup/ec2/montagu-barman-keypair',
                                 field='KeyMaterial')

    @property
    def target_private_key(self):
        """Returns the key that the ec2 instance uses to SSH to production."""
        return self._read_secret('secret/backup/ec2/target-keypair',
                                 field='KeyMaterial')

    @property
    def target_host_key(self):
        """Returns the public key of the production machine"""
        return self._read_secret('secret/backup/ec2/target-host-key')

    def get_password(self, user):
        return self._read_secret('secret/database/production/users/{}'.format(
            user), field='password')

    def get_barman_passwords(self):
        return {
            "barman": self.get_password("barman"),
            "streaming_barman": self.get_password("streaming_barman")
        }
