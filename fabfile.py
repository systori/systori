import os
from fabric.api import env, run, local, cd, get, prefix, sudo


env.hosts = ['ubrblik.de']


def deploy(env_name='dev'):
    assert env_name in ['dev', 'production']

    if env_name == 'production':
        yes=raw_input('Deploying to PRODUCTION. Are you sure? (type "yes"): ')
        if not yes == 'yes':
            print 'Canceling.'
            return

    sudo('service uwsgi stop ubrblik_'+env_name)

    with cd('/srv/ubrblik/'+env_name+'/ubrblik-editor'):
        run('git pull')
        run('/usr/lib/dart/bin/pub get')
        run('/usr/lib/dart/bin/pub build')

    with cd('/srv/ubrblik/'+env_name+'/ubrblik'):
        with prefix('source ../bin/activate'):
            run('git pull')
            run('pip install --upgrade -r requirements/%s.pip'%env_name)
            sudo('./manage.py migrate --noinput', user='www-data')
            run('./manage.py collectstatic --noinput')

    sudo('service uwsgi start ubrblik_'+env_name)

def _reset_localdb():
    local('dropdb ubrblik_local')
    local('createdb ubrblik_local')

def localdb_from_bootstrap():
    _reset_localdb()
    local('./manage.py migrate')
    local('./manage.py loaddata bootstrap')

prod_dump_path = '/tmp/ubrblik.prod.dump'
prod_dump_file = os.path.basename(prod_dump_path)
def fetch_productiondb():
    dbname = 'ubrblik_production'
    # -Fc : custom postgresql compressed format
    sudo('pg_dump -Fc -f %s %s' % (prod_dump_path,dbname), user='www-data')
    get(prod_dump_path, prod_dump_file)
    sudo('rm %s'%prod_dump_path)

def load_productiondb():
    _reset_localdb()
    local('pg_restore -d ubrblik_local -O '+prod_dump_file)

def localdb_from_productiondb():
    fetch_productiondb()
    load_productiondb()
    local('rm '+prod_dump_file)

def init_settings(env_name='local'):
    assert env_name in ['dev', 'production', 'local']
    if os.path.exists('ubrblik/settings/__init__.py'):
        print('Settings have already been initialized.')
    else:
        with open('ubrblik/settings/__init__.py', 'w') as s:
            print('Initializing settings for {}'.format(env_name))
            s.write('from .{} import *\n'.format(env_name))


def make_messages():
    local('./manage.py makemessages -l de -e tex,html,py')


def mail():
    local('python -m smtpd -n -c DebuggingServer localhost:1025')
