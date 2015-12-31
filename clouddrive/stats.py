from datetime import datetime
import os

from BTrees.OOBTree import OOBTree
from clouddrive import db
from persistent.dict import PersistentDict
import transaction


def record_stats(root, counts):
    db.update()
    root['last_run'] = counts
    if 'stats' not in root:
        root['stats'] = OOBTree({
            'uploaded': 0,
            'ignored': 0,
            'errored': 0
            })
    root['stats'].update(counts)
    root['stats']['last_run_datetime'] = datetime.utcnow().isoformat()


def record_action(root, what):
    db.update()
    root['action'] = {
        'what': what,
        'when': datetime.utcnow().isoformat()
    }
    transaction.commit()


def record_filestart(filename):
    db.update()
    root = db.get()
    root['current_file'] = PersistentDict({
        'filename': filename,
        'percent': 0,
        'filesize': os.stat(filename).st_size
    })
    transaction.commit()


def record_fileprogress(done, total):
    db.update()
    percent = int((float(done) / float(total)) * 100)
    root = db.get()
    if 'current_file' in root:
        root['current_file']['percent'] = percent
        transaction.commit()


def record_filedone():
    db.update()
    root = db.get()
    if 'current_file' in root:
        del root['current_file']
        transaction.commit()