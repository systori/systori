### About Ubrblik ###

Ubrblik is a suite of tools for construction companies to create project estimates, to manage those projects and generate invoices.

Server side is written in [Python](https://www.python.org/) using the [Django framework](https://www.djangoproject.com/) with [PostgreSQL](http://www.postgresql.org/) as the backing database.

Desktop client side is written using Django templates and [Dart](https://www.dartlang.org/). The task editor has a separate repository here: [ubrblik-editor](https://bitbucket.org/damoti/ubrblik-editor)

Mobile client is written in Dart using the [Polymer framework](https://www.polymer-project.org/) and [Google's port of Cordova](https://github.com/MobileChromeApps/mobile-chrome-apps). The mobile client repository is located here: [ubrblik-mobile](https://bitbucket.org/damoti/ubrblik-mobile)

The rest of this guide will focus on the Django app. See links above for information on getting setup with task editor and mobile client.

### How do I get set up? ###

This guide assumes you are on the most recent LTS Ubuntu linux system and that you already have git and SSH keys setup with bitbucket.org.

You will need PostgreSQL, Python3 and some other tools installed with apt-get:

```console
$ apt-get install\
 postgresql postgresql-contrib postgresql-server-dev-all\
 python-pip python-dev python3-dev\
 texlive-full
$ sudo pip install --upgrade fabric virtualenvwrapper
```

Now change into the directory where you'd like to install ubrblik and run the following commands:

```console
$ git clone git@bitbucket.org:damoti/ubrblik.git
$ cd ubrblik/
$ mkvirtualenv -a `pwd` -p /usr/bin/python3 ubrblik
```

Now setup the database and run some tests:

```console
$ createdb ubrblik_local
$ ./manage.py syncdb
$ ./manage.py test
```

When you are done working on ubrblik, you can deactivate the virtual environment:

```console
$ deactive
```

And the next time you want to activate it run:

```console
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
