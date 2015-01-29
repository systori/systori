import os
from fabric.api import env, run, local, cd, lcd, prefix, sudo, settings


env.hosts = ['ubrblik.damoti.com' if env.user == 'lex' else 'ubrblik.de']


def deploy(env_name='dev'):
    assert env_name in ['dev', 'prod']

    if env_name == 'prod':
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


def resetlocaldb():
    local('dropdb ubrblik_local')
    local('createdb ubrblik_local')
    local('./manage.py migrate')
    local('./manage.py loaddata bootstrap')


def init_settings(env_name='local'):
    assert env_name in ['dev', 'prod', 'local']
    if os.path.exists('ubrblik/settings/__init__.py'):
        print('Settings have already been initialized.')
    else:
        with open('ubrblik/settings/__init__.py', 'w') as s:
            print('Initializing settings for {}'.format(env_name))
            s.write('from .{} import *\n'.format(env_name))


def makemessages():
    local('./manage.py makemessages -l de -e tex,html,py')


def mail():
    local('python -m smtpd -n -c DebuggingServer localhost:1025')
