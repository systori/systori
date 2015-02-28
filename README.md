### About Ubrblik ###

Ubrblik is a suite of tools for construction companies to create project estimates, to manage those projects and generate invoices.

Server side is written in [Python](https://www.python.org/) using the [Django framework](https://www.djangoproject.com/) with [PostgreSQL](http://www.postgresql.org/) as the backing database.

Desktop client side is written using Django templates and [Dart](https://www.dartlang.org/).

The rest of this guide will focus on the Django app. See links above for information on getting setup with task editor and mobile client.

### How do I get set up? ###

This guide assumes you are on the most recent LTS Ubuntu linux system and that you already have git and SSH keys setup with bitbucket.org.

You will need PostgreSQL, Python3 and some other tools installed with apt-get:

```
$ sudo apt-get install\
 postgresql postgresql-contrib postgresql-server-dev-all\
 python-pip python-dev python3-dev\
 texlive-full
$ sudo pip install --upgrade fabric virtualenvwrapper
$ source /usr/local/bin/virtualenvwrapper.sh
$ echo "source /usr/local/bin/virtualenvwrapper.sh" > ~/.bashrc

# install needed locales
```

Create a database user; when the databse user name matches your linux user name this allows `psql` and other tools to automatically authenticate you:

```
$ sudo -u postgres createuser --superuser [YOUR_LINUX_USERNAME]
```

Now change into the directory where you'd like to install ubrblik and run the following commands:

```
$ git clone git@bitbucket.org:damoti/ubrblik.git
$ cd ubrblik/
$ mkvirtualenv -a `pwd` -p /usr/bin/python3 ubrblik
$ pip install -r requirements/dev.pip
$ fab init_settings
```

Now run some tests to make sure everything is working:

```
$ ./manage.py test
```

Finally setup a database for local development and start the app:

```
$ createdb ubrblik_local
$ ./manage.py migrate
$ ./manage.py runserver
```

When you are done working on ubrblik, you can deactivate the virtual environment:

```
$ deactive
```

And the next time you want to activate it run (this will automatically place you in the ubrblik checkout directory):

```
$ workon ubrblik
```


### Contribution guidelines ###

* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)
* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact