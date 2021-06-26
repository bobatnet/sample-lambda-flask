import base64
import os

import boto3
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def client_info():
    client = boto3.client('cloudformation')

    def query(res) -> str:
        res = client.describe_stack_resource(
            StackName=os.environ['STACK_NAME'], LogicalResourceId=res)
        return res['StackResourceDetail']['PhysicalResourceId']

    users, client, myapi, secret = query('Users'), query(
        'LoginClient'), query('MyApi'), query("TokenCookieSecret")

    client_secret = boto3.client('cognito-idp').describe_user_pool_client(
        UserPoolId=users,
        ClientId=client
    )['UserPoolClient']['ClientSecret']

    secret = secret.encode()
    salt = secret[:16]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
    )
    cookie_encrypt_key = base64.urlsafe_b64encode(kdf.derive(secret[16:]))

    return users, client, client_secret, myapi, cookie_encrypt_key


users, client_id, client_secret, myapi, secret_key = client_info()

crypter = Fernet(secret_key)

headers = {
    "Authorization": "Basic " + (base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8"))).decode(),
    "Content-Type": "application/x-www-form-urlencoded"
}

url = f"https://{os.environ['DOMAIN_NAME']}.auth.us-east-2.amazoncognito.com"

redir_url = f"https://{myapi}.execute-api.us-east-2.amazonaws.com/{os.environ['STAGENAME']}/home/"


def get_tokens(code):
    resp = requests.post(url + "/oauth2/token", params={
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'redirect_uri': redir_url,
    },
        headers=headers
    )

    try:
        resp.raise_for_status()
    except Exception:
        print(resp.text)
        raise
    return resp.json()
