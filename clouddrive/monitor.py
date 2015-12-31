import json
import os
import sys
import time

from BTrees.OOBTree import OOBTree
from clouddrive import api
from clouddrive import db
from clouddrive import stats
import mimetypes
from persistent.list import PersistentList
import transaction
from dateutil.parser import parse as parse_date
from fnmatch import fnmatch


def get_virtual_root(root_node):
    path = 'nodes?filters=kind:FOLDER AND parents:%s' % (
        root_node['id']
    )
    virtual_root_resp = api.call(path, 'metadata')
    if virtual_root_resp['count'] == 0:
        sub_folder = db.get()['config']['sub_folder']
        return api.call('nodes', 'metadata', 'POST', {
            'name': sub_folder,
            'kind': 'FOLDER',
            'parents': [root_node['id']]
        })
    return virtual_root_resp['data'][0]


def build_index():
    root_node = api.get_root_folder()['data'][0]
    root = db.get()
    root['root_node'] = root_node
    virtual_root = get_virtual_root(root_node)
    index = OOBTree(virtual_root)

    def process_folder(folder):
        if 'children' not in folder:
            folder['children'] = OOBTree()
        result = api.call('nodes/%s/children' % folder['id'], 'metadata')
        if len(result) == 0:
            return
        for node in result['data']:
            node = OOBTree(node)
            folder['children'][node['name']] = node
            if node['kind'] == 'FOLDER':
                process_folder(node)

    process_folder(index)
    db.update()
    root['index'] = index
    transaction.commit()


def get_folder_node(folder):
    root = db.get()
    current = root['index']
    for part in folder.split('/')[1:]:
        found = False
        for node in current['children'].values():
            if node['name'] == part:
                current = node
                found = True
                break
        if not found:
            # parents = current['parents'] + [current['id']]
            new = api.call('nodes', 'metadata', 'POST', {
                'name': part,
                'kind': 'FOLDER',
                'parents': [current['id']]
            })
            if new.get('code') == 'NAME_ALREADY_EXISTS':
                _id = new['info']['nodeId']
                new = api.call('nodes/' + _id, 'metadata')
            db.update()
            new = OOBTree(new)
            new['children'] = OOBTree()
            current['children'][new['name']] = new
            current = new
    return current


def upload_file(filepath, folder_node):
    stats.record_filestart(filepath)
    filename = filepath.split('/')[-1]
    _type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    result = api.call('nodes?suppress=deduplication', method='POST', body={
        'metadata': json.dumps({
            'name': filename,
            'kind': 'FILE',
            'parents': [folder_node['id']]
            })
        },
        body_type='data',
        args={
            'files': [('content', (filename, open(filepath, 'rb'), _type))]
        }
    )
    stats.record_filedone()
    return result


def overwrite_file(filepath, folder_node, _id):
    stats.record_filestart(filepath)
    filename = filepath.split('/')[-1]
    _type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    result = api.call('nodes/%s/content' % _id, method='PUT', args={
        'files': [('content', (filename, open(filepath, 'rb'), _type))]
    })
    stats.record_filedone()
    return result


def sync_folder(_folder, counts):

    def _sync_folder(folder):
        db.update()
        config = db.get()['config']
        excluded = config['excluded']
        folder_node = get_folder_node(folder)
        transaction.commit()
        for filename in os.listdir(folder):
            if filename[0] == '.':
                continue
            filepath = os.path.join(folder, filename)
            dive_out = False
            for excluded_path in excluded:
                if fnmatch(filepath, excluded_path):
                    dive_out = True
                    break
            if dive_out:
                continue
            if os.path.isdir(filepath):
                _sync_folder(filepath)
                continue
            if '.' not in filename:
                continue

            try:
                if filename in folder_node['children']:
                    node = folder_node['children'][filename]
                    updated = parse_date(node['modifiedDate'])
                    if os.stat(filepath).st_mtime < updated.timestamp():
                        counts['ignored'] += 1
                        continue
                    result = overwrite_file(filepath, folder_node, node['id'])
                    counts['uploaded'] += 1
                else:
                    result = upload_file(filepath, folder_node)
                    counts['uploaded'] += 1
                    if result.get('code') == 'NAME_ALREADY_EXISTS':
                        result = overwrite_file(filepath, folder_node,
                                                result['info']['nodeId'])
            except:
                result = {}
            if 'id' not in result:
                root = db.get()
                if 'errored' not in root:
                    root['errored'] = PersistentList()
                root['errored'].append(filepath)
                root['errored'] = root['errored'][-20:]
                counts['errored'] += 1
                continue
            db.update()
            folder_node['children'][result['name']] = result
            transaction.commit()

    _sync_folder(_folder)


def sync():
    counts = {
        'ignored': 0,
        'uploaded': 0,
        'errored': 0
    }
    config = db.get()['config']
    for folder in config.get('folders', []):
        if os.path.exists(folder):
            sync_folder(folder, counts)
    return counts


def run(argv=sys.argv):
    root = db.get()
    while not api.get_credentials():
        stats.record_action(root, 'Application not authorized')
        time.sleep(30)

    while True:
        while 'config' not in root:
            time.sleep(5)
            root = db.get()

        if 'metadata' not in root:
            metadata = root['metadata'] = OOBTree()
        else:
            metadata = root['metadata']
        if (time.time() - metadata.get('endpoint_last_retrieved', 0)) > (60 * 60 * 24 * 3):
            api.store_endpoint()

        if (time.time() - metadata.get('index_last_built', 0)) > (60 * 60 * 24 * 5):
            stats.record_action(root, 'Building index')
            metadata['index_last_built'] = time.time()
            build_index()

        stats.record_action(root, 'Syncing files')
        stats.record_stats(root, sync())

        stats.record_action(root, 'Packing database')
        storage = db.get_storage()
        storage.pack(time.time(), wait=True)

        stats.record_action(root, 'Taking a break for 30 minutes...')
        time.sleep(60 * 30)