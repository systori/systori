import os
import sys
import json
from distutils.version import LooseVersion as _V
from fabric.api import env, run, cd, local, lcd, get, prefix, sudo

from version import VERSION


version = _V(VERSION)


env.hosts = ['systori.com']


deploy_apps = {
    'dev': ['dev'],
    'production': ['production']
}

PROD_MEDIA_PATH = '/srv/systori/production'
PROD_MEDIA_FILE = 'systori.media.tgz'


def deploy(envname='dev'):
    ":envname=dev -- deploy code to remote server"
    env.user = 'ubrblik'

    for app in deploy_apps[envname]:

        sudo('service uwsgi stop systori_' + app)

        with cd('/srv/systori/' + app + '/systori'):

            if envname == 'dev':
                # load production db
                sudo('dropdb systori_dev', user='www-data')
                sudo('createdb systori_dev', user='www-data')
                sudo('pg_dump -f prod.sql systori_production', user='www-data')
                sudo('psql -f prod.sql systori_dev >/dev/null', user='www-data')
                sudo('rm prod.sql')

            run('git pull')

            with cd('systori/dart'):
                run('/usr/lib/dart/bin/pub get')
                run('/usr/lib/dart/bin/pub build')

            with prefix('source ../bin/activate'):
                run('pip install -q -U -r requirements/%s.pip' % envname)
                sudo('./manage.py migrate --noinput', user='www-data')
                run('./manage.py collectstatic --noinput --verbosity 0')

        sudo('service uwsgi start systori_' + app)

    slack('push to <%(systori-url)s|%(envname)s> finished', envname)


def makemessages():
    "django makemessages"
    local('./manage.py makemessages -l de -e tex,html,py')


def test():
    "django test"
    local('./manage.py test --keepdb systori')


def fetchdb(envname='production'):
    ":envname=production -- fetch remote database, see getdb"
    dbname = 'systori_'+envname
    dump_file = 'systori.'+envname+'.dump'
    # -Fc : custom postgresql compressed format
    sudo('pg_dump -Fc -x -f /tmp/%s %s' % (dump_file, dbname), user='www-data')
    get('/tmp/' + dump_file, dump_file)
    sudo('rm /tmp/' + dump_file)


def getdb(envname='production'):
    ":envname=production -- fetch and load remote database"
    fetchdb(envname)
    local('dropdb systori_local')
    local('createdb systori_local')
    local('pg_restore -d systori_local -O systori.'+envname+'.dump')
    local('rm systori.'+envname+'.dump')


def getmedia():
    "download production media files"
    with cd(PROD_MEDIA_PATH):
        run('tar -cz media -f /tmp/' + PROD_MEDIA_FILE)
    get('/tmp/' + PROD_MEDIA_FILE, PROD_MEDIA_FILE)
    local('tar xfz ' + PROD_MEDIA_FILE)
    local('rm ' + PROD_MEDIA_FILE)
    run('rm /tmp/' + PROD_MEDIA_FILE)


def dockergetdb(container='web', envname='production'):
    ":container=web,envname=production -- fetch and load remote database"
    dump_file = 'systori.'+envname+'.dump'
    settings = {
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db_1'
    }
    fetchdb(envname)
    local('docker-compose run {0} dropdb -h {HOST} -U {USER} {NAME}'.format(
        container, **settings))
    local('docker-compose run {0} createdb -h {HOST} -U {USER} {NAME}'.format(
        container, **settings))
    local('docker-compose run {0} pg_restore -d {NAME} -O {1} -h {HOST} -U {USER}'.format(
        container, dump_file, **settings))
    local('rm ' + dump_file)


def initsettings(envname='local'):
    ":envname=local -- creates __init__.py in settings folder"
    assert envname in ['dev', 'production', 'local', 'jenkins']
    if os.path.exists('systori/settings/__init__.py'):
        print('Settings have already been initialized.')
    else:
        with open('systori/settings/__init__.py', 'w') as s:
            print('Initializing settings for {}'.format(envname))
            s.write('from .{} import *\n'.format(envname))


def getdart():
    "download latest version of dart"
    is_64bits = sys.maxsize > 2**32
    BIN_DIR = os.path.expanduser('~/bin')
    if not os.path.exists(BIN_DIR):
        os.mkdir(BIN_DIR)
    url = (
        'http://storage.googleapis.com/dart-archive/channels'
        '/stable/release/latest/sdk/dartsdk-linux-%s-release.zip'
    ) % ('x64' if is_64bits else 'ia32')
    with lcd(BIN_DIR):
        local("curl %s > dartsdk.zip" % url)
        local("unzip -qo dartsdk.zip")
    env_lines = """\
export DART_SDK="%s"
export PATH="$HOME/.pub-cache/bin:$DART_SDK/bin:$PATH"
""" % os.path.join(BIN_DIR, 'dart-sdk')
    bash_rc_file = os.path.expanduser('~/.bashrc')
    if not os.path.exists(bash_rc_file):
        print("Add to your environment:")
        print(env_lines)
    elif not 'DART_SDK' in open(bash_rc_file, 'r').read():
        with open(bash_rc_file, 'a') as file_handle:
            file_handle.write(env_lines)


def linkdart():
    "create .packages file"
    with open('systori/dart/.packages', 'r') as packages:
        for package in packages:
            if package.startswith('#'):
                continue
            package_name, location = package.strip().split(':', 1)
            location = '/' + location.lstrip('file:///')
            try:
                os.symlink(location, os.path.join('systori/dart/web/packages', package_name))
            except OSError, exc:
                print exc


def makedart():
    "build dart packages in debug mode"
    with lcd('systori/dart'):
        local('pub build --mode=debug')


def testdart():
    "run dart tests"
    with lcd('systori/dart'):
        local('pub run test -r expanded -p content-shell test')


SLACK = 'https://hooks.slack.com/services/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'


def slack(msg, envname='dev'):
    import requests
    middomain = '' if envname=='production' else '.'+envname
    systori_url = 'https://mehr-handwerk'+middomain+'.systori.com'
    requests.post(SLACK, json.dumps({'text':
        msg % {'systori-url': systori_url, 'envname': envname}
    }))


def mail():
    "start mail debugging server"
    local('python -m smtpd -n -c DebuggingServer localhost:1025')


def jenkins():

    local('pip install --upgrade -r requirements/dev.pip')

    initsettings('jenkins')

    with lcd('systori/dart'):
        local('/usr/lib/dart/bin/pub get')
        local('/usr/lib/dart/bin/pub build')

    local('coverage run -p manage.py test systori')
    local('coverage combine')
    local('coverage html')

    slack('build finished')
