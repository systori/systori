import os
import sys
import json
from distutils.version import LooseVersion as _V
from fabric.api import env, run, cd, local, lcd, get, prefix, sudo
from fabric.context_managers import shell_env

from version import VERSION


version = _V(VERSION)

env.hosts = ['systori.com']

PROD_MEDIA_PATH = '/var/lib/systori/production'
PROD_MEDIA_FILE = 'systori.media.tgz'


def prepare(service, branch):
    "copy database and migrate"

    settings = {
        'HOST': 'db',
        'NAME': 'systori_{}'.format(service),
        'USER': 'postgres'
    }

    if service != 'production':
        local('dropdb -h {HOST} -U {USER} {NAME}'.format(**settings))
        local('createdb -T systori_production -h {HOST} -U {USER} {NAME}'.format(**settings))

    local('./manage.py migrate --noinput')
    local('psql -c "VACUUM ANALYZE" -h {HOST} -U {USER} {NAME}'.format(**settings))


def uwsgi():
    "start uwsgi service"
    local("uwsgi"
          " --module=systori.wsgi"
          " --socket=0.0.0.0:8000"
          " --static-map /static=/static"
          " --attach-daemon=\"celery -A systori worker -B\""
          " --env DJANGO_SETTINGS_MODULE={}".format(
              os.environ['DJANGO_SETTINGS_MODULE']))


def test():
    "django continuous integration test"
    with shell_env(DJANGO_SETTINGS_MODULE='systori.settings.test'):
        local('coverage run -p manage.py test -v 2 systori.apps systori.lib')
        local('coverage combine')
        local('coverage html -d reports')


def makemessages():
    "django makemessages"
    local('./manage.py makemessages -l de -e tex,html,py')


def fetchdb(envname='production'):
    ":envname=production -- fetch remote database, see getdb"
    container = 'systori_db_1'
    dbname = 'systori_'+envname
    dump_file = 'systori.'+envname+'.dump'
    dump_folder = '/var/lib/postgresql/dumps'
    dump_path = os.path.join(dump_folder, dump_file)
    # -Fc : custom postgresql compressed format
    run('docker exec {container} pg_dump -U postgres -Fc -x -f {dump_path} {dbname}'
        .format(**locals()))
    get(dump_path, dump_file)
    sudo('rm {}'.format(dump_path))


def dbexists(name):
    dbs = local('psql -lqt | cut -d \| -f 1', capture=True).split()
    return name in dbs


def getdb(envname='production'):
    ":envname=production -- fetch and load remote database"
    fetchdb(envname)
    if dbexists('systori_local'):
        local('dropdb systori_local')
    local('createdb systori_local')
    local('pg_restore -d systori_local -O systori.'+envname+'.dump')
    local('psql -c "ANALYZE" systori_local')
    local('rm systori.'+envname+'.dump')


def getmedia():
    "download production media files"
    with cd(PROD_MEDIA_PATH):
        run('tar -cz media -f /tmp/' + PROD_MEDIA_FILE)
    get('/tmp/' + PROD_MEDIA_FILE, PROD_MEDIA_FILE)
    local('tar xfz ' + PROD_MEDIA_FILE)
    local('rm ' + PROD_MEDIA_FILE)
    run('rm /tmp/' + PROD_MEDIA_FILE)


def dockergetdb(container='app', envname='production'):
    ":container=app,envname=production -- fetch and load remote database"
    dump_file = 'systori.'+envname+'.dump'
    settings = {
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db'
    }
    fetchdb(envname)
    local('docker-compose stop app')
    local('docker-compose run {0} dropdb -h {HOST} -U {USER} {NAME}'.format(
        container, **settings))
    local('docker-compose run {0} createdb -h {HOST} -U {USER} {NAME}'.format(
        container, **settings))
    local('docker-compose run {0} pg_restore -d {NAME} -O {1} -h {HOST} -U {USER}'.format(
        container, dump_file, **settings))
    local('rm ' + dump_file)


def localdockergetdb(container='app', envname='production'):
    """\
    :container=app,envname=production -- fetch and load remote database
    Useful for setups where the app is run locally and postgresql is dockerized
    """
    dump_file = 'systori.'+envname+'.dump'
    settings = {
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'localhost'
    }
    fetchdb(envname)
    local('dropdb -h {HOST} -U {USER} {NAME}'.format(
        container, **settings))
    local('createdb -h {HOST} -U {USER} {NAME}'.format(
        container, **settings))
    local('pg_restore -d {NAME} -O {1} -h {HOST} -U {USER}'.format(
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


def getdartium(version='1.22.0-dev.7.0', channel='dev'):
    "get dartium and content-shell for linux, on Mac use homebrew"

    BIN = os.path.expanduser('~/bin')
    DOWNLOAD = os.path.join(BIN, 'downloads')
    if not os.path.exists(BIN):
        os.mkdir(BIN)
    if not os.path.exists(DOWNLOAD):
        os.mkdir(DOWNLOAD)

    paths = []
    with lcd(BIN):

        for app in ('content_shell', 'dartium',):

            zipfile = os.path.join(DOWNLOAD, '{}-{}-{}.zip'.format(app, version, channel))

            if not os.path.exists(zipfile):
                url = (
                    'https://storage.googleapis.com/dart-archive/channels/{}/release/'
                    '{}/dartium/{}-linux-x64-release.zip'.format(channel, version, app)
                )
                local("curl {} > {}".format(url, zipfile))

            outdir = local('unzip -l {} | head -n 4 | tail -n 1'.format(zipfile), capture=True)
            outdir = outdir.split(' ')[-1]

            if not os.path.exists(os.path.join(BIN, outdir)):
                local("unzip -qo {}".format(zipfile))
                if app == 'dartium':
                    with lcd(outdir):
                        local("ln -s chrome dartium")

            local("ln -sfn {} {}".format(outdir, app))
            paths.append(os.path.join(BIN, app))

        lib = 'libfontconfig1_2.11.0-0ubuntu4.2_amd64.deb'
        libfile = os.path.join(DOWNLOAD, lib)
        if not os.path.exists(libfile):
            liburl = (
                'http://security.ubuntu.com/ubuntu/pool/main/f/fontconfig/'+lib
            )
            local("curl {} > {}".format(liburl, libfile))

        local(
            "dpkg --fsys-tarfile {} | tar xOf - ./usr/lib/x86_64-linux-gnu/libfontconfig.so.1.8.0"
            " > content_shell/lib/libfontconfig.so.1".format(libfile)
        )

    not_present = [path for path in paths if path not in os.environ['PATH']]
    if not_present:
        print("Add to your environment:")
        print('export PATH="%s:$PATH"' % ':'.join(not_present))


def linkfonts():
    TRUETYPE = '/usr/share/fonts/truetype'
    FONTS = {
        'msttcorefonts': {
            'fonts': [
                'Arial', 'Comic_Sans_MS', 'Courier_New', 'Georgia', 'Impact',
                'Trebuchet_MS', 'Times_New_Roman', 'Verdana',
            ],
            'variants': ['', '_Bold', '_Italic', '_Bold_Italic']
        },
        'kochi': {'fonts': ['kochi-gothic', 'kochi-mincho']},
        'ttf-indic-fonts-core': {'fonts': ['lohit_hi', 'lohit_ta', 'MuktiNarrow']},
        'ttf-punjabi-fonts': {'fonts': ['lohit_pa']}
    }

    if not os.path.exists(os.path.join(TRUETYPE, 'ttf-dejavu')):
        local('sudo ln -s {} {}'.format(
            os.path.join(TRUETYPE, 'dejavu'),
            os.path.join(TRUETYPE, 'ttf-dejavu'),
        ))

    for family, fonts in FONTS.items():
        family_path = os.path.join(TRUETYPE, family)
        if not os.path.exists(family_path):
            local('sudo mkdir {}'.format(family_path))
        with lcd(family_path):
            for font in fonts['fonts']:
                for variant in fonts.get('variants', ['']):
                    font_file = font+variant+'.ttf'
                    font_path = os.path.join(family_path, font_file)
                    if not os.path.exists(font_path):
                        local('sudo ln -s ../dejavu/DejaVuSans-Bold.ttf {}'.format(font_file))


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
            except OSError as exc:
                print(exc)


def makedart():
    "build dart packages in debug mode"
    with lcd('systori/dart'):
        local('pub build --mode=debug')


def testdart(test_file=None):
    "run dart tests"
    with lcd('systori/dart'):
        docker = "docker run --rm -v `pwd`:`pwd` --workdir=`pwd` damoti/content-shell"
        if test_file:
            local(docker + " '-r expanded {}'".format(test_file))
        else:
            local(docker)


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


def dockercontextsize():
    "shows size of 'context' uploaded to docker when building docker image"
    local('du -X .dockerignore -h -d 2 | sort -h')


def jenkins():

    local('pip install --upgrade -r requirements/dev.pip')

    initsettings('jenkins')

    with lcd('systori/dart'):
        local('pub get')
        #local('pub build') we'll need this later when doing selenium tests
        local("xvfb-run -s '-screen 0 1024x768x24' pub run test -r expanded -p content-shell test")

    local('coverage run -p manage.py test systori')
    local('coverage combine')
    local('coverage html')

    slack('build finished')

def git():
    "git usage help and cheatsheet"
    print("Start a new branch (based on dev)...")
    print("git checkout -b <new_branch> dev")
