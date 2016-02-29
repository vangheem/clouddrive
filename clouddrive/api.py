import time

from BTrees.OOBTree import OOBTree
from clouddrive import db
from clouddrive import configurator
import requests
import transaction
from urllib.parse import urlencode


LOGIN_URL = 'https://www.amazon.com/ap/oa'
AUTH_URL = 'https://api.amazon.com/auth/o2/token'

SCOPES = [
    'clouddrive:read_all',
    'clouddrive:write'
]
DRIVE_ENDPOINT = 'https://drive.amazonaws.com'


def get_login_url(redirect_uri):
    params = {
        'client_id': configurator.CLIENT_ID,
        'scope': ' '.join(SCOPES),
        'redirect_uri': redirect_uri,
        'response_type': 'code'
    }
    return '%s?%s' % (
        LOGIN_URL,
        urlencode(params))


def authorize(code, redirect_uri):
    params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': configurator.CLIENT_ID,
        'client_secret': configurator.CLIENT_SECRET,
        'redirect_uri': redirect_uri
    }
    resp = requests.post(AUTH_URL, data=params)
    store_credentials(resp.json())
    return resp.json()


def refresh():
    tokens = get_credentials()
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token'],
        'client_id': configurator.CLIENT_ID,
        'client_secret': configurator.CLIENT_SECRET
    }
    resp = requests.post(AUTH_URL, data=params)
    store_credentials(resp.json())


def store_credentials(data):
    root = db.get()
    root['credentials'] = data
    transaction.commit()


def get_credentials():
    root = db.get()
    if 'credentials' in root:
        return root['credentials']


def store_endpoint():
    root = db.get()
    uri = '%s/drive/v1/account/endpoint' % DRIVE_ENDPOINT
    creds = get_credentials()
    resp = requests.get(uri, headers={
        'Authorization': 'Bearer ' + creds['access_token']
    })
    if 'metadata' in root:
        metadata = root['metadata']
    else:
        metadata = root['metadata'] = OOBTree()
    data = resp.json()
    if data.get('message') == 'Token has expired':
        refresh()
        return store_endpoint()
    metadata['endpoint'] = data
    metadata['endpoint_last_retrieved'] = time.time()
    transaction.commit()


def call(path, endpoint_type='content', method='GET', body=None,
         body_type='json', args=None):
    root = db.get()

    metadata = root.get('metadata', {})
    endpoint = metadata.get('endpoint', {})

    if endpoint.get('message') == 'Token has expired' or metadata == {}:
        refresh()
        store_endpoint()
        root._p_jar.sync()
        metadata = root.get('metadata', {})
        endpoint = metadata.get('endpoint', {})

    if endpoint_type == 'content':
        endpoint = endpoint.get('contentUrl')
    else:
        endpoint = endpoint.get('metadataUrl')
    if not endpoint:
        return
    uri = '%s/%s' % (endpoint.rstrip('/'), path.lstrip('/'))
    creds = get_credentials()
    meth = requests.get
    if method == 'POST':
        meth = requests.post
    elif method == 'PUT':
        meth = requests.put
    if args is None:
        args = {}
    if body:
        args[body_type] = body
    resp = meth(uri, headers={
        'Authorization': 'Bearer ' + creds['access_token']
    }, **args)
    if resp.status_code == 401:
        refresh()
        return call(path, endpoint_type, method, body, body_type, args)
    return resp


def list_files():
    return call('nodes?filters=kind:FOLDER', 'metadata').json()


def get_root_folder():
    return call('nodes?filters=kind:FOLDER AND isRoot:true', 'metadata').json()
