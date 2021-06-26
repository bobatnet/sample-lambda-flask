from . import app


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    req_path = event['path'].rstrip('/')

    with app.test_client() as cl:
        print(req_path)
        resp = cl.get(req_path)

        token = None
        try:
            token = event['requestContext']['authorizer']['id_token_secure']
        except KeyError:
            pass
        else:
            resp.set_cookie('TOKEN', value=token, secure=True,
                            httponly=True)

        data, status_code = resp.data, resp.status_code

        return {
            'statusCode': status_code,
            'body': data,
            'headers': dict(resp.headers)
        }
