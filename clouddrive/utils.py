from clouddrive import db


def get_node(path):
    node = db.get()['index']
    parts = path.rstrip('/').split('/')
    for part in parts:
        node = node['children'][part]
    return node
