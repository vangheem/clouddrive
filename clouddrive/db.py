import threading

from ZEO import ClientStorage
from ZODB import DB
import transaction

_thread_data = threading.local()


def get_storage():
    try:
        return _thread_data.zodb_storage
    except AttributeError:
        addr = '127.0.0.1', 5001
        storage = _thread_data.zodb_storage = ClientStorage.ClientStorage(addr)
        return storage


def get_conn():
    try:
        return _thread_data.zodb_conn
    except AttributeError:
        db = DB(get_storage())
        _thread_data.zodb_conn = db.open()
        return _thread_data.zodb_conn


def get():
    conn = get_conn()
    return conn.root()


def update():
    get()._p_jar.sync()


def update_and_commit():
    update()
    transaction.commit()