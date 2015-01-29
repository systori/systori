Prerequisites
=============
Most things from the developer instructions are required such as python3, postgresql, latex, git+bitbucket access, etc.

Also Dart: [Install Instructions](https://www.dartlang.org/tools/debian.html)

Install Ubrblik on Dev/Production Server
========================================

```
sudo apt-get install nginx uwsgi uwsgi-plugin-python3

mkdir -p /srv/ubrblik/{dev,production}/
sudo echo 127.0.0.101 dev_ubrblik >> /etc/hosts
sudo echo 127.0.0.102 production_ubrblik >> /etc/hosts

cd /srv/ubrblik/dev/
git clone git@bitbucket.org:damoti/ubrblik-editor.git
cd ubrblik-editor
/usr/lib/dart/bin/pub get
/usr/lib/dart/bin/pub build

cd /srv/ubrblik/dev/
git clone git@bitbucket.org:damoti/ubrblik.git
virtualenv -p /usr/bin/python3 /srv/ubrblik/dev/
source bin/activate
cd ubrblik
fab init_settings:env_name=dev
pip install -r requirements/dev.pip
createdb -O www-data ubrblik_dev
# modify /etc/passwd so that www-data has a shell
# this is probably a security issue, should find
# better way to do this
sudo su www-data
source ../bin/activate
./manage.py migrate
./manage.py loaddata bootstrap
./manage.py collectstatic --noinput
exit # logout www-data

sudo cp server/dev_ubrblik.ini /etc/uwsgi/apps-available/
cd /etc/uwsgi/apps-enabled/
sudo ln -s /etc/uwsgi/apps-available/dev_ubrblik.ini
sudo service uwsgi start dev_ubrblik
cd -

sudo cp server/dev.ubrblik.de /etc/nginx/sites-available/
cd /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/dev.ubrblik.de
sudo service nginx restart
```
