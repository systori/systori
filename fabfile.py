import os
from distutils.version import LooseVersion as V
from fabric.api import env, run, local, cd, get, prefix, sudo
import requests

from version import VERSION
version = V(VERSION)

env.hosts = ['ubrblik.de']
env.user = 'ubrblik'

deploy_apps = {
  'dev': ['dev'],
  'production': ['demo', 'mehr_handwerk']
}


def deploy(env_name='dev'):

    for app in deploy_apps[env_name]:

        sudo('service uwsgi stop ubrblik_'+app)

        with cd('/srv/ubrblik/'+app+'/ubrblik'):

            if env_name == 'dev':
                # load production db
                sudo('dropdb ubrblik_dev', user='www-data')
                sudo('createdb ubrblik_dev', user='www-data')
                sudo('pg_dump -f prod.sql ubrblik_mehr_handwerk', user='www-data')
                sudo('psql -f prod.sql ubrblik_dev >/dev/null', user='www-data')
                sudo('psql -c "update document_proposal set email_pdf = substr(email_pdf, 33), print_pdf = substr(print_pdf, 33);" ubrblik_dev', user='www-data')
                sudo('rm prod.sql')
                # copy production documents
                run('cp -p -r /srv/ubrblik/mehr_handwerk/ubrblik/documents documents')

            run('git pull')

            with cd('editor'):
                run('/usr/lib/dart/bin/pub get')
                run('/usr/lib/dart/bin/pub build')

            with prefix('source ../bin/activate'):
                run('pip install -q -U -r requirements/%s.pip'%env_name)
                sudo('./manage.py migrate --noinput', user='www-data')
                run('./manage.py collectstatic --noinput --verbosity 0')

        sudo('service uwsgi start ubrblik_'+app)


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
    dbname = 'ubrblik_mehr_handwerk'
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

def get_bitbucket_login():
    try:
        user, password = open('bitbucket.login').read().split(':')
        return user.strip(), password.strip()
    except:
        print 'Bitbucket API requires your user credentials'
        user = raw_input('Username: ') or exit(1)
        password = raw_input('Password: ') or exit(1)
        saved = '{}:{}'.format(user, password)
        open('bitbucket.login','w').write(saved)
        return user, password


REPO = 'https://api.bitbucket.org/1.0/repositories/damoti/ubrblik/'
def current_issues():
    r = requests.get(REPO+'issues?status=new', auth=get_bitbucket_login())
    print r.status_code
    print r.text


def mail():
    local('python -m smtpd -n -c DebuggingServer localhost:1025')


# Git Workflow
# See: http://nvie.com/posts/a-successful-git-branching-model/


def bump_version(ver):
    with file('version.py', 'w') as f:
        f.write('VERSION = \'%s\'' % ver)
    print('Bumped version number to %s' % ver)


def feature_start(name):
    "fab feature_start:name=my_new_feature"
    local('git checkout -b %s dev' % name)


def feature_finish(name):
    "fab feature_finish:name=my_new_feature"
    local('git checkout dev')
    local('git merge --no-ff %s' % name)
    local('git branch -d %s' % name)
    local('git push origin dev')


def release_start(ver):
    branch = 'release-%s' % ver
    local('git checkout -b %s dev' % branch)
    if VERSION != ver:
        bump_version(ver)
    with settings(warn_only=True):
        local('git commit -a -m "bumped version number to %s"' % ver)
    local('git push origin %s' % branch)


def release_finish():
    _merge_this()


def hotfix_start(bump='yes'):
    sub_number = version.version[1] + (bump == 'yes' and 1 or 0)
    new_ver = '%s.%s' % (version.version[0], sub_number)
    local('git checkout -b hotfix-%s master' % new_ver)
    if bump == 'bump':
        bump_version(new_ver)
        local('git commit version.py -m "bumped version number to %s"' % new_ver)


def hotfix_finish():
    _merge_this()


def _merge_this():
    '''
    Merge current branch into both master and dev branches, then delete it.
    Meant to be called from commands
    '''
    # Parsing branch version: (release|hotfix)-<major>.<minor>
    branch = local('git rev-parse --abbrev-ref HEAD', capture=True).rstrip()
    if branch in ('master', 'dev'):
        abort('''Your current branch is %s, which is one of the main branches. 
            Try checking out your hotfix/release branch.''' % branch)
    # Trying to figure out version from current branch name
    ver = branch.split('-')
    ver = len(ver) > 1 and ver[-1] or None
    # Merging into prod branch
    local('git checkout master')
    local('git merge --no-ff %s' % branch)
    if ver:
        # Updating prod branch tag
        local('git tag -a -f -m "{v}" {v}'.format(v=ver))
    local('git push')
    # Merging into dev
    local('git checkout dev')
    local('git merge --no-ff %s' % branch)
    # Killing this branch
    with settings(warn_only=True):
        local('git push origin :%s' % branch)
    local('git branch -d %s' % branch)
    local('git push')

