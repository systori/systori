import os
from fabric.api import env, run, local, cd, lcd, prefix, sudo, settings

env.hosts = ['ubrblik.de']

def deploy():
    sudo('service uwsgi stop ubrblik')

    with cd('/srv/ubrblik.de/ubrblik'):
        with prefix('source ../bin/activate'):

            run('hg pull -u')

            #run('pip install --upgrade -r requirements/prod.pip')

            #run('dropdb ubrblik_production')
            #run('createdb -O www-data ubrblik_production')
            #sudo('./manage.py migrate --migrate --noinput', user='www-data')
            #sudo('./manage.py loaddata bootstrap', user='www-data')
            #run('./manage.py collectstatic --noinput')
            #run('./manage.py compress')

    sudo('service uwsgi start ubrblik')


def resetlocaldb():
    local('dropdb ubrblik_local')
    local('createdb ubrblik_local')
    local('./manage.py migrate --noinput')
    #local('./manage.py loaddata bootstrap')


#def resettestdb():
#    local('dropdb test_ubrblik_local')
#    local('createdb test_ubrblik_local')
#    local('./manage.py migrate --settings=ubrblik.settings.test --migrate --noinput')
#    local('./manage.py loaddata --settings=ubrblik.settings.test bootstrap')


def init_settings(env_name='local'):
    assert env_name in ['dev', 'prod', 'local']
    if os.path.exists('ubrblik/settings/__init__.py'):
        print('Settings have already been initialized.')
    else:
        with open('ubrblik/settings/__init__.py', 'w') as s:
            print('Initializing settings for {}'.format(env_name))
            s.write('from .{} import *\n'.format(env_name))


def mail():
    local('python -m smtpd -n -c DebuggingServer localhost:1025')
