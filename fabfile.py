import os.path as op
import importlib
import sys
from urllib.parse import urlparse
from collections import namedtuple

from fabric.api import put, settings, run, env, local, get
from fabric.context_managers import cd, lcd, shell_env
from fabric.contrib import files
from fabric.operations import prompt

PROJ = 'router'
HOST = '188.227.72.189'
FILES = [
    PROJ + '_uwsgi.py',
    PROJ + '_uwsgi.ini',
    'requirements.txt',
]

LOCAL_ROOT = op.dirname(op.realpath(__file__))
sys.path.insert(0, op.join(LOCAL_ROOT, PROJ))
# Importing config as a standalone file, not within PROJ module:
try:
    config = importlib.import_module('config')
except ImportError:
    config = None
REMOTE_ROOT = '/home/{}'.format(PROJ)
NGINX = PROJ + '.nginx'
SYSTEMD = PROJ + '_uwsgi.service'

env.hosts = [HOST]
env.user = PROJ
env.shell = '/bin/bash -c'  # dropped -l flag
env.colorize_errors = True


def psql(command, locally=False):
    command = 'psql -c "{}"'.format(command)
    sent = 'sudo -u postgres {}'.format(command)
    with settings(user='root'):
        (local if locally else run)(sent)


def _create_user(username, password, locally=False):
    cmd = '''CREATE USER "{username}" WITH PASSWORD '{password}';'''
    psql(cmd.format(**locals()), locally=locally)


def _create_database(dbname, username, locally=False):
    psql(
        '''CREATE DATABASE "{dbname}" WITH encoding='utf8'
           template="template0"
           LC_COLLATE='ru_RU.UTF-8'
           LC_CTYPE='ru_RU.UTF-8';'''
        .format(**locals()), locally=locally
    )
    psql(
        '''GRANT ALL PRIVILEGES ON DATABASE "{dbname}" to "{username}";'''
        .format(**locals()), locally=locally
    )


def setup_nginx():
    with settings(user='root'), lcd(LOCAL_ROOT):
        put(NGINX, '/etc/nginx/sites-available/')
        run('ln -s -f /etc/nginx/sites-available/{} '
            '/etc/nginx/sites-enabled/'.format(NGINX))
        run('nginx -t')
        run('systemctl reload nginx')


def _db():
    DB = namedtuple('DB', 'uri dbname username password')
    uri = config.SQLALCHEMY_DATABASE_URI
    db = urlparse(uri)
    dbname = db.path.lstrip('/')
    return DB(uri, dbname, db.username, db.password)


def setup_db(locally=False):
    db = _db()
    _create_user(db.username, db.password, locally=locally)
    _create_database(db.dbname, db.username, locally=locally)


def restore_db_to_local():
    x = prompt('This will destroy local DB. Are you sure?', default='N')
    if x.lower() not in ['yes', 'y']:
        print('Exiting')
        return
    db = _db()
    outfile = 'temp-dump.sql'
    with settings(user=db.username), cd('/tmp'), lcd(LOCAL_ROOT), \
            shell_env(LC_ALL='ru_RU.UTF-8'):
        run(
            'pg_dump --create --clean {} > {}'
            .format(db.dbname, outfile)
        )
        get(outfile, '.')
        run('rm -f {}'.format(outfile))
        local('sudo -u postgres psql < {}'.format(outfile))
        local('rm -f {}'.format(outfile))


def setup_systemd():
    with settings(user='root'), lcd(LOCAL_ROOT):
        put(SYSTEMD, '/etc/systemd/system/')
        run('systemctl enable {}'.format(SYSTEMD))
        run('systemctl start {}'.format(SYSTEMD))


def reload():
    with settings(user='root'):
        run('systemctl restart {}'.format(SYSTEMD))


def download_config():
    with cd(REMOTE_ROOT), lcd(LOCAL_ROOT):
        get('{}/config.py'.format(PROJ), PROJ)


def deploy(setup=False, db=False):
    if config is None:
        raise Exception('Local config.py missing')

    if db:
        setup_db()
    run('mkdir -p {}'.format(REMOTE_ROOT))

    with cd(REMOTE_ROOT), lcd(LOCAL_ROOT):
        run('mkdir -p logs')

        for filename in FILES:
            put(filename, '.')

        local('find . -type d -name __pycache__ -prune -exec rm -R -f {} \;')
        run('rm -R -f {}'.format(PROJ))
        put(PROJ, '.')
        run('chmod -R o-rwx {}'.format(PROJ))

        if not files.exists('venv'):
            run('python3 -m venv venv')

        run('venv/bin/pip3 install --upgrade pip')
        run('venv/bin/pip3 install -r requirements.txt')

        run('venv/bin/python3 -c "from {} import db; db.create_all()"'.format(PROJ))

    if setup:
        setup_systemd()
        setup_nginx()
    reload()
