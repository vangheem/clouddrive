import sys

from clouddrive import api
from clouddrive import configurator
from clouddrive import db
from clouddrive import utils
from clouddrive import patches  # noqa
import flask as f
import transaction
from flask import jsonify


app = f.Flask('clouddrive')
app.debug = True


@app.route("/")
def index():
    if not api.get_credentials():
        url = utils.get_url('auth_callback', '/authcallback', True)
        return f.redirect(api.get_login_url(url))
    root = db.get()
    root._p_jar.sync()
    config = root.get('config', {})
    configured = configurator.valid(config)
    action = root.get('action', {})
    what = action.get('what')
    when = action.get('when')
    current = root.get('current_file')
    return f.render_template(
        'index.html', configured=configured, what=what,
        when=when, current_file=current,
        errored=root.get('errored', [])[-20:], **config)


@app.route("/status")
def status():
    root = db.get()
    root._p_jar.sync()
    config = root.get('config', {})
    configured = configurator.valid(config)
    action = root.get('action', {})
    what = action.get('what')
    when = action.get('when')
    current = root.get('current_file')
    return jsonify(
        configured=configured, what=what,
        when=when, current_file=current,
        errored=root.get('errored', [])[-20:], **config)


def _export_node(node):
    data = {}
    for key, val in node.items():
        if key == 'children':
            continue
        data[key] = val
    return data


@app.route("/browse")
def browse():
    root = db.get()
    root._p_jar.sync()
    path = f.request.args.get('path')
    if path == '/':
        node = db.get()['index']
    else:
        node = utils.get_node(path)

    data = _export_node(node)
    data['children'] = []
    data['path'] = path
    if path == '/':
        path = ''
    for key, child in node['children'].items():
        node = _export_node(child)
        node['path'] = path + '/' + key
        data['children'].append(node)
    return jsonify(**data)


@app.route("/download")
def download():
    _id = f.request.args.get('id')
    result = api.call('nodes/' + _id, 'metadata', 'GET', body={'tempLink': 'true'}).json()
    return jsonify(url=result['tempLink'])


@app.route("/authcallback")
def auth_callback():
    """
    http://localhost/?code=ANdNAVhyhqirUelHGEHA&scope=clouddrive%3Aread_all+clouddrive%3Awrite
    """
    db.get()._p_jar.sync()
    code = f.request.args.get('code')
    auth_callback_url = utils.get_url('auth_callback', '/authcallback', True)
    configure_url = utils.get_url('configure_view', '/configure', True)
    api.authorize(code, auth_callback_url)
    return f.redirect(configure_url)


@app.route("/configure", methods=['POST', 'GET'])
def configure_view():
    error = False
    saved = False
    if f.request.method == 'POST':
        config = {}
        for field in configurator.fieldnames:
            value = f.request.form.get(field)
            if not value:
                error = True
            else:
                if field in configurator.list_fields:
                    value = value.splitlines()
            config[field] = value
        if not error:
            root = db.get()
            root._p_jar.sync()
            root['config'] = config
            transaction.commit()
            saved = True
    return f.render_template(
        'configure.html', error=error, saved=saved,
        **configurator.get_config_with_defaults())


def run_server(argv=sys.argv):
    app.run()
