import os

import hvac

DEFAULT_VAULT_ADDR = "https://support.montagu.dide.ic.ac.uk:8200"


def vault_client():
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


def get_private_key():
    vault = vault_client()
    secret = vault.read('secret/backup/ec2/montagu-barman-keypair')
    return secret['data']['KeyMaterial']