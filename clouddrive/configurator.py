from copy import deepcopy
from clouddrive import db
import os
from configparser import ConfigParser

DIR = os.path.dirname(os.path.realpath(__file__))
PACKAGE_DIR = '/'.join(DIR.split('/')[:-1])

config = ConfigParser()
config.readfp(open(os.path.join(PACKAGE_DIR, 'config.ini')))

CLIENT_ID = config.get('config', 'client_id')
CLIENT_SECRET = config.get('config', 'client_secret')
UPLOAD_RATE = int(config.get('config', 'upload_rate'))
SERVER_URL = config.get('server_url', None)

fieldnames = (
    'sub_folder',
    'folders',
    'excluded',
    'update_frequency')
list_fields = (
    'folders',
    'excluded')
_defaults = {
    'sub_folder': 'foobar',
    'folders': ['/Users/foobar'],
    'excluded': [
        '*/Dropbox/*',
        '*/bin/*',
        '*/Google Drive/*',
        '*/buildout-cache/*',
        '*/VirtualBox VMs/*',
        '*/eggs/*',
        '*/Downloads/*',
        '*/Library/*',
        '*_rsa*',
        '*/blobstorage/*',
        '*/filestorage/*',
        '*.app',
        '*.dmg',
        '*.img',
        '*.iso',
        '*.localized',
        '*.bin',
        '*.po',
        '*.pub',
        '*.pyc',
        '*.dll',
        '*.class',
        '*.o',
        '*.so',
        '*.lo',
        '*.la',
        '*.rej',
        '*.pyo',
        '*/__pycache__/*',
        '*.DS_Store',
        '*.DS_Store?',
        '*ehthumbs.db',
        '*Thumbs.db',
        '*.tmproj',
        '*~*',
        '*.sw[op]',
        '*.egg-info',
        '*.egg-info.installed.cfg',
        '*.pt.py',
        '*.cpt.py',
        '*.zpt.py',
        '*.html.py',
        '*.egg',
        '*.mr.developer.cfg',
        '*.installed.cfg',
        '*.project',
        '*.pydevproject',
        '*.settings',
        '*.idea',
        '*.codeintel',
        '*/parts/*',
        '*/develop-eggs/*'
    ],
    'update_frequency': 60 * 24
}


def valid(config):
    for field_name in fieldnames:
        if not config.get(field_name):
            return False
    return True


def get_config_with_defaults():
    root = db.get()
    config = root.get('config', {})
    defaults = deepcopy(_defaults)
    for key in fieldnames:
        value = config.get(key)
        if not value:
            config[key] = defaults[key]
    return config
