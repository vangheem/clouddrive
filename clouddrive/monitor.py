from BTrees.OOBTree import OOBTree
from clouddrive import api
from clouddrive import commands
from clouddrive import db
from clouddrive import stats
from datetime import datetime
from dateutil.parser import parse as parse_date
from fnmatch import fnmatch
from persistent.list import PersistentList

import json
import mimetypes
import os
import sys
import time
import transaction


def get_virtual_root(root_node):
    path = 'nodes?filters=kind:FOLDER AND parents:%s' % (
        root_node['id']
    )
    virtual_root_resp = api.call(path, 'metadata').json()
    names = [n['name'] for n in virtual_root_resp['data']]
    sub_folder = db.get()['config']['sub_folder']
    if sub_folder not in names:
        return api.call('nodes', 'metadata', 'POST', {
            'name': sub_folder,
            'kind': 'FOLDER',
            'parents': [root_node['id']]
        }).json()
    else:
        for node in virtual_root_resp['data']:
            if node['name'] == sub_folder:
                return node


def build_index():
    root_node = api.get_root_folder()['data'][0]
    root = db.get()
    root['root_node'] = root_node
    virtual_root = get_virtual_root(root_node)
    index = OOBTree(virtual_root)

    def process_folder(folder):
        if 'children' not in folder:
            folder['children'] = OOBTree()
        result = api.call('nodes/%s/children' % folder['id'], 'metadata').json()
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
            }).json()
            if new.get('code') == 'NAME_ALREADY_EXISTS':
                _id = _get_id(new)
                new = api.call('nodes/' + _id, 'metadata').json()
            db.update()
            new = OOBTree(new)
            new['children'] = OOBTree()
            current['children'][new['name']] = new
            current = new
    return current


def upload_file(filepath, folder_node):
    stats.record_filestart(filepath)
    filename = filepath.split('/')[-1].replace('"', 'quote').replace("'", 'quote')
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
    ).json()
    stats.record_filedone()
    return result


def overwrite_file(filepath, folder_node, _id):
    stats.record_filestart(filepath)
    filename = filepath.split('/')[-1].replace('"', 'quote').replace("'", 'quote')
    _type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    result = api.call('nodes/%s/content?suppress=deduplication' % _id, method='PUT', args={
        'files': [('content', (filename, open(filepath, 'rb'), _type))]
    }).json()
    stats.record_filedone()
    return result


def files_match(filepath, node):
    node_md5 = node.get('md5')
    if node_md5 is None:
        node.get('contentProperties', {}).get('md5')
    if node_md5 is None:
        # check against size
        updated = parse_date(node['modifiedDate'])
        return os.stat(filepath).st_mtime < updated.timestamp()
    else:
        return commands.md5(filepath) == node_md5


def _get_id(node):
    _id = node.get('id')
    if _id is None:
        return node.get('info', {}).get('id')
    return _id


def sync_folder(_folder, counts):

    def _sync_folder(folder):
        db.update()
        config = db.get()['config']
        excluded = config['excluded']
        try:
            update_frequency = int(config.get('update_frequency', 60 * 60 * 24))
        except:
            update_frequency = 60 * 60 * 24
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
                    if files_match(filepath, node):
                        counts['ignored'] += 1
                        continue
                    update_frequency
                    updated = parse_date(node['modifiedDate'])
                    if os.stat(filepath).st_mtime > (updated.timestamp() + update_frequency):
                        counts['ignored'] += 1
                        continue
                    result = overwrite_file(filepath, folder_node, node['id'])
                    counts['uploaded'] += 1
                else:
                    md5 = commands.md5(filepath)
                    # we don't have file in index, check if it is already uploaded first
                    result = api.call('nodes?filters=contentProperties.md5:%s' % md5,
                                      endpoint_type='metadata').json()
                    found = False
                    if len(result['data']) > 0:
                        for node in result['data']:
                            if node['parents'][0] == folder_node['id']:
                                result = node
                                found = True
                                break

                    if not found:
                        result = upload_file(filepath, folder_node)
                        counts['uploaded'] += 1
                        _id = _get_id(result)
                        if result.get('code') == 'NAME_ALREADY_EXISTS':
                            existing = api.call('nodes/' + _id, 'metadata', 'GET').json()
                            existing_md5 = existing.get('md5')
                            if existing_md5 is None:
                                existing_md5 = existing.get('contentProperties', {}).get('md5')
                            if existing_md5 == md5:
                                counts['ignored'] += 1
                                result = existing
                            else:
                                result = overwrite_file(filepath, folder_node,
                                                        _get_id(result))
            except:
                result = {}
            if _get_id(result) is None:
                root = db.get()
                if 'errored' not in root:
                    root['errored'] = PersistentList()
                root['errored'].append(filepath)
                root['errored'] = root['errored'][-20:]
                counts['errored'] += 1
                continue
            db.update()
            folder_node['children'][filename] = result
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


def get_deleted_folder(path):
    dt = datetime.now()
    folder_path = '/'.join(path.split('/')[:-1])
    return os.path.join(
        '/DELETED/%i/%i' % (dt.year, dt.month),
        folder_path.lstrip('/'))


def move_node(old_parent, new_parent, node):
    db.update()
    del old_parent['children'][node['name']]
    if new_parent['id'] not in node['parents']:
        node['parents'] = [new_parent['id']]
    if 'children' not in new_parent:
        new_parent['children'] = OOBTree()
    new_parent['children'][node['name']] = node
    transaction.commit()


def clean():
    root = db.get()

    def process(path, node, parent):
        if 'DELETED' in path:
            return
        if node['kind'] == 'FILE':
            # check if exists
            if not os.path.exists(path):
                # XXX move to deleted folder
                deleted_folder = get_folder_node(get_deleted_folder(path))
                resp = api.call(
                    'nodes/%s/children' % deleted_folder['id'], method='POST',
                    endpoint_type='metadata', body={
                        'fromParent': parent['id'],
                        'childId': node['id']}
                )
                if resp.status_code == 200:
                    move_node(parent, deleted_folder, resp.json())
                elif resp.status_code == 400:
                    data = resp.json()
                    if data['code'] == 'INVALID_PARENT':
                        if data['info']['parentId'] == deleted_folder['id']:
                            # already moved, now move the node
                            move_node(parent, deleted_folder, node)
        else:
            # go through and process each child
            if 'children' not in node:
                return
            for name, child in node['children'].items():
                child_path = os.path.join(path, name)
                process(child_path, child, node)

    process('/', root['index'], None)


def initialize_db():
    root_node = api.get_root_folder()['data'][0]
    root = db.get()
    root['root_node'] = root_node
    virtual_root = get_virtual_root(root_node)
    index = OOBTree(virtual_root)
    db.update()
    root['index'] = index


def _run(argv=sys.argv):
    root = db.get()
    while not api.get_credentials():
        stats.record_action(root, 'Application not authorized')
        time.sleep(5)

    if 'index' not in root:
        initialize_db()

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

        # reset errors
        root['errored'] = []
        transaction.commit()

        stats.record_action(root, 'Syncing files')
        stats.record_stats(root, sync())

        stats.record_action(root, 'Cleaning files')
        stats.record_stats(root, clean())

        stats.record_action(root, 'Packing database')
        storage = db.get_storage()
        storage.pack(time.time(), wait=True)

        stats.record_action(root, 'Taking a break for 10 minutes...')
        time.sleep(60 * 10)


def run(argv=sys.argv):
    while True:
        try:
            _run()
        except:
            db.update()
            root = db.get()
            root['errored'] = []
            transaction.commit()
            time.sleep(60 * 5)
