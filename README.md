[![Build Status](https://magnum.travis-ci.com/systori/systori.svg?token=euxuNjuxx7RiAnuoQpWu&branch=dev)](https://magnum.travis-ci.com/systori/systori)
[![Coverage Status](https://coveralls.io/repos/systori/systori/badge.svg?branch=dev&service=github&t=VAhuEl)](https://coveralls.io/github/systori/systori?branch=dev)  


## About Systori

Systori is a suite of tools for craftsmen to create project estimates, to manage those projects and generate invoices.

Server side is written in [Python](https://www.python.org/) using the [Django framework](https://www.djangoproject.com/) with [PostgreSQL](http://www.postgresql.org/) as the backing database.

Desktop client side is written using Django templates and [Dart](https://www.dartlang.org/).

## How do I get set up?

### Workstation

This guide assumes you are on the most recent **Ubuntu LTS** linux system and that you already have git and SSH keys setup with github.com.

You will need PostgreSQL, Python3 and some other tools installed with apt-get:

```
$ sudo apt-get install\
 postgresql postgresql-contrib postgresql-server-dev-all\
 python-pip python-dev python3-dev python3-lxml mercurial libjpeg-dev
$ sudo apt-get build-dep python3-lxml
$ sudo pip install --upgrade fabric virtualenvwrapper
$ source /usr/local/bin/virtualenvwrapper.sh
$ echo "source /usr/local/bin/virtualenvwrapper.sh" > ~/.bashrc

$ sudo apt-get install language-pack-de
```

Create a database user; when the databse user name matches your linux user name this allows `psql` and other tools to automatically authenticate you:

```
$ sudo -u postgres createuser --superuser [YOUR_LINUX_USERNAME]
```

Now change into the directory where you'd like to install systori and run the following commands:

```
$ git clone git@github.com:systori/systori.git
$ cd systori/
$ mkvirtualenv -a `pwd` -p /usr/bin/python3 systori
```
Set ssh to point to github with every subdomain
```
vi /etc/ssh/ssh_config
-> add the following:
Host *github.com
 HostName github.com
```
Install requirements and init settings
```
$ pip install -r requirements/dev.pip
$ fab initsettings
```

Now run some tests to make sure everything is working:

```
$ ./manage.py test
```

Finally setup a database for local development and start the app:

```
$ createdb systori_local
$ fab localdb_from_productiondb
```

When you are done working on systori, you can deactivate the virtual environment:

```
$ deactive
```

And the next time you want to activate it run (this will automatically place you in the systori checkout directory):

```
$ workon systori
```


## Development Environment

For development of systori you can use either PyCharm or PyDev.


### Install Oracle Java 7

```
$ sudo add-apt-repository ppa:webupd8team/java
$ sudo apt-get update
$ sudo apt-get install oracle-java7-installer
```


### PyCharm

1. Get PyCharm: https://www.jetbrains.com/pycharm/download/

2. Extract PyCharm.

3. Install Dart plugin.

#### Database Access

If you want to use the Database tool in PyCharm to access the local database it's easiest if you disable password authentication in postgresql.

Edit pg_hba.conf, `sudo vi /etc/postgresql/9.3/main/pg_hba.conf` changing the host 127.0.0.1 line to be:

    host    all             all             127.0.0.1/32            trust

Then restart postgres, `/etc/init.d/postgresql restart`.

You should now be able to connect and browse the `systori_local` database.

### Code guidelines ###

Indentation [spaces]:

Language : Tab size : Indent : Continuation indent

* Pyhton : 4 : 4 : 8

* Dart : 4 : 4 : 8

* HTML : 2 : 2 : 4

* CSS : 2 : 2 : 4

### Contribution guidelines ###

* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)
* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact

### Systori color palette ###

|Color      | 100%    | 75%     | 50%     | 25%    |
|-----------|---------|---------|---------|--------|
|Brown      | #BBA892 | #CCBEAD | #DDD3C8 | #EEE9E3|
|Red        | #D41351 | #E05E76 | #EA99A2 | #F5CFD1|
|Orange     | #EE725F | #F39985 | #F8BDAD | #FCE0D6|
|Yellow     | #FAB94B | #FCCB7E | #FEDDAB | #FFEED6|
|BlueGreen  | #006C7C | #478A98 | #8AACB8 | #C6D4DA|
|Green      | #00A19A | #6CB7B3 | #A6CFCC | #D5E7E6|
|Mint       | #B7DBC1 | #CBE4D2 | #DDEDE1 | #EEF6F1|
