import os

import hvac

DEFAULT_VAULT_ADDR = "https://support.montagu.dide.ic.ac.uk:8200"

vault = None


def vault_client():
    global vault
    if not vault:
        vault_url = os.environ.get("VAULT_ADDR", DEFAULT_VAULT_ADDR)
        vault_token = os.environ.get("VAULT_AUTH_GITHUB_TOKEN")
        if not vault_token:
            print("Please paste your vault GitHub access token: ", end="")
            vault_token = input().strip()
        vault = hvac.Client(url=vault_url)
        print("Authenticating vault with GitHub")
        vault.auth_github(vault_token)
    return vault


def save_securely(path, data):
    with open(path, 'a'):  # Create file if does not exist
        pass
    os.chmod(path, 0o600)
    with open(path, 'w') as f:
        f.write(data)


def get_ec2_private_key():
    """Returns the key that we use to SSH into the ec2 instance.
    The instance is set up to trust this key by the KeyName parameter in
    create_instance. Amazon holds the public key and is able to inject it
    into authorized_keys on each new instance."""
    vault = vault_client()
    secret = vault.read('secret/backup/ec2/montagu-barman-keypair')
    return secret['data']['KeyMaterial']


def get_target_private_key():
    """Returns the key that the ec2 instance uses to SSH to production."""
    vault = vault_client()
    secret = vault.read('secret/backup/ec2/target-keypair')
    return secret['data']['KeyMaterial']


def get_target_host_key():
    """Returns the public key of the production machine"""
    vault = vault_client()
    secret = vault.read('secret/backup/ec2/target-host-key')
    return secret['data']['value']
