from clouddrive import db
import flask as f
from clouddrive import configurator


def get_node(path):
    node = db.get()['index']
    parts = path.rstrip('/').split('/')
    for part in parts:
        node = node['children'][part]
    return node


def get_url(name, path, _external=False):
    if configurator.SERVER_URL:
        return configurator.SERVER_URL.rstrip('/') + '/' + path.lstrip('/')
    return f.url_for(name, _external=_external)
