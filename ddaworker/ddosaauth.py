from functools import wraps
from flask import request, Response
import os

import logging

logger=logging.getLogger(__name__)

def get_server_auth():
    s={}
    for n,m in [
            ('env', lambda:os.environ.get("SECRET_DDOSA_SERVER")),
            ('homefile', lambda:open(os.environ['HOME']+"/.secret-ddosa-server").read().strip()),
           ]:
        try:
            return 'remoteintegral', m()
        except Exception as e:
            logger.debug(f"failed to get auth from {n}")
            s[n]=repr(e)

    raise Exception(f"unable to setup worker auth: {s}")

server_auth=get_server_auth()

def check_auth(username, password):
    return username == server_auth[0] and password == server_auth[1]

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated