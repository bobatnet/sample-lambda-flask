import re

from .encrypt_token import get_tokens, crypter
from .user_validator import get_claims


def lambda_handler(event, context):
    print(event)

    permit = 'Deny' or 'Allow'
    token = None
    context_out = {}

    if qparams := event.get('queryStringParameters', None):
        if code := qparams.get('code', None):
            token = get_tokens(code)['id_token']
            id_token_secure = crypter.encrypt(token.encode())
            permit = 'Allow'
            context_out['id_token_secure'] = id_token_secure

    elif headers := event.get('headers', None):
        if cookie_ := headers.get('Cookie', None):
            for cook in cookie_.split(';'):
                if token := re.match(" ?TOKEN=(.*)", cook):

                    token_ = crypter.decrypt(token.group(1).encode())
                    claims = get_claims(token_.decode())
                    if claims:
                        permit = 'Allow'
                        context_out.update(claims)

    return {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": permit,
                    "Resource": "*"
                }
            ]
        },
        "context": context_out,
    }
