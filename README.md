## About Systori

Systori is a suite of tools for craftsmen to create project estimates, to manage those projects and generate invoices.

Server side is written in [Python](https://www.python.org/) using the [Django framework](https://www.djangoproject.com/) with [PostgreSQL](http://www.postgresql.org/) as the backing database.

Desktop client side is written using Django templates and [Dart](https://www.dartlang.org/).

## How do I get set up?

### Workstation

This guide assumes you are on the most recent **Ubuntu LTS** linux system and that you already have git and SSH keys setup with bitbucket.org.

You will need PostgreSQL, Python3 and some other tools installed with apt-get:

```
$ sudo apt-get install\
 postgresql postgresql-contrib postgresql-server-dev-all\
 python-pip python-dev python3-dev\
 texlive-full python3-lxml git
$ sudo apt-get build-dep python3-lxml
$ sudo pip install --upgrade fabric virtualenvwrapper
$ source /usr/local/bin/virtualenvwrapper.sh
$ echo "source /usr/local/bin/virtualenvwrapper.sh" > ~/.bashrc

$ # install needed locales
```

Create a database user; when the databse user name matches your linux user name this allows `psql` and other tools to automatically authenticate you:

```
$ sudo -u postgres createuser --superuser [YOUR_LINUX_USERNAME]
```

Now change into the directory where you'd like to install systori and run the following commands:

```
$ git clone git@bitbucket.org:damoti/systori.git
$ cd systori/
$ mkvirtualenv -a `pwd` -p /usr/bin/python3 systori
$ pip install -r requirements/dev.pip
$ fab init_settings
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


### Option 1. PyCharm

1. Get PyCharm: https://www.jetbrains.com/pycharm/download/

2. Extract PyCharm.

3. Install Dart plugin.

#### Database Access

If you want to use the Database tool in PyCharm to access the local database it's easiest if you disable password authentication in postgresql.

Edit pg_hba.conf, `sudo vi /etc/postgresql/9.3/main/pg_hba.conf` changing the host 127.0.0.1 line to be:

    host    all             all             127.0.0.1/32            trust

Then restart postgres, `/etc/init.d/postgresql restart`.

You should now be able to connect and browse the `systori_local` database.


### Option 2. Eclipse

#### Install Eclipse

1. Download latest [Eclipse IDE for Java Developers](http://www.eclipse.org/downloads/)


1. Create a **bin** directory in home and extract eclipse:


        $ mkdir ~/bin
        $ cd ~/bin
        $ tar xzf ../Downloads/eclipse-java-mars-M6-linux-gtk.tar.gz


1. Edit ```eclipse.ini```...


    Add GTK version to fix rendering bug (should be two lines just like below):


        --launcher.GTK_version
        2


    Change memory amounts:


        -XX:MaxPermSize=512m
        -Xms512m
        -Xmx1024m


1. Open text editor with new file ```~/bin/eclipse.desktop``` and add the following content making sure to replace **[YOUR_USER_NAME]** with your user name:


        [Desktop Entry]
        Version=1.0
        Type=Application
        Name=Eclipse 
        Icon=/home/[YOUR_USER_NAME]/bin/eclipse/icon.xpm
        Exec=/home/[YOUR_USER_NAME]/bin/eclipse/eclipse


1. Open file manager (Nautilus) and find the file you created above. Drag the file onto the Ubuntu Unity side bar.


#### Install Plugins

1. Start eclipse, open menu: ```Help -> Install New Software...```

1. Make sure *Work with:* shows the standard eclipse update site (eg. **Mars**).

1. Now install:

    * Web, XML, Java EE and OSGi Enterprise Development

        * **Eclipse Web Developer Tools**
        * **JavaScript Development Tools**

1. Add PyDev update site and install PyDev:

    * Name: **PyDev**

    * Location: **http://pydev.org/updates**

1. Add Vrapper update site (vim emulator for eclipse) and install it:

    * Name: **Vrapper**

    * Location: **http://vrapper.sourceforge.net/update-site/stable**

1. Add Mylyn Bitbucket update site and install it:

    * Name: **Mylyn Bitbucket**

    * Location: **http://babelserver.org/mylyn-bitbucket/**

1. Add Dart Editor update site and install it:

    * Name: **Dart Editor**

    * Location: **http://www.dartlang.org/eclipse/update/channels/dev/**

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