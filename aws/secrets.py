import os

from vault.vault import VaultClient


def save_securely_to_disk(path, data):
    with open(path, 'a'):  # Create file if does not exist
        pass
    os.chmod(path, 0o600)
    with open(path, 'w') as f:
        f.write(data)


class AWSVaultClient(VaultClient):
    @property
    def ec2_private_key(self):
        """Returns the key that we use to SSH into the ec2 instance.
        The instance is set up to trust this key by the KeyName parameter in
        create_instance. Amazon holds the public key and is able to inject it
        into authorized_keys on each new instance."""
        return self.read_secret('secret/vimc/backup/ec2/montagu-barman-keypair',
                                field='KeyMaterial')

    @property
    def target_private_key(self):
        """Returns the key that the ec2 instance uses to SSH to production."""
        return self.read_secret('secret/vimc/backup/ec2/target-keypair',
                                field='KeyMaterial')

    @property
    def target_host_key(self):
        """Returns the public key of the production machine"""
        return self.read_secret('secret/vimc/backup/ec2/target-host-key')

    def get_password(self, user):
        return self.read_secret('secret/vimc/database/production/users/{}'.format(
            user), field='password')

    def get_barman_passwords(self):
        return {
            "barman": self.get_password("barman"),
            "streaming_barman": self.get_password("streaming_barman")
        }
