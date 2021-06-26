from . import app

with app.test_client() as cl:
    resp = cl.get('/home')

    print(resp.data)
