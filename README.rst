.. image:: systori_logo.svg
   :width: 10%
   :align: center
   :alt: Systori logo

======================================================
|codecov| |travis| |python| |codestyle| |style-check| |chat|
======================================================

Systori is a suite of tools for craftsmen to create project estimates, to manage those projects, and to generate invoices.
Server side is written in Python_ using the `Django framework`_ with PostgreSQL_ as the backing database.
Client side is written using Django templates and Dart_.

Installation and usage
----------------------
This is a standard Django app with, currently, some Dart for the Client. If you have questions how to get started please get in touch.

Code guidelines
---------------

Indentation [spaces]:

Language : Tab size : Indent : Continuation indent

* Pyhton : 4 : 4 : 8

* Dart : 4 : 4 : 8

* HTML : 2 : 2 : 4

* CSS : 2 : 2 : 4

Contribution guidelines
-----------------------

* Writing tests
* Code review
* Other guidelines

Systori color palette
---------------------
+-----------+---------+---------+---------+--------+
|Color      | 100%    | 75%     | 50%     | 25%    |
+===========+=========+=========+=========+========+
|Brown      | #BBA892 | #CCBEAD | #DDD3C8 | #EEE9E3|
+-----------+---------+---------+---------+--------+
|Red        | #D41351 | #E05E76 | #EA99A2 | #F5CFD1|
+-----------+---------+---------+---------+--------+
|Orange     | #EE725F | #F39985 | #F8BDAD | #FCE0D6|
+-----------+---------+---------+---------+--------+
|Yellow     | #FAB94B | #FCCB7E | #FEDDAB | #FFEED6|
+-----------+---------+---------+---------+--------+
|BlueGreen  | #006C7C | #478A98 | #8AACB8 | #C6D4DA|
+-----------+---------+---------+---------+--------+
|Green      | #00A19A | #6CB7B3 | #A6CFCC | #D5E7E6|
+-----------+---------+---------+---------+--------+
|Mint       | #B7DBC1 | #CBE4D2 | #DDEDE1 | #EEF6F1|
+-----------+---------+---------+---------+--------+













.. _Python: https://www.python.org
.. _Django Framework: https://www.djangoproject.com/
.. _PostgreSQL: https://www.postgresql.org/
.. _Dart: https://www.dartlang.org/

.. |codecov| image:: https://img.shields.io/codecov/c/github/systori/systori/dev.svg
   :target: https://codecov.io/gh/systori/systori
   :alt: Test Coverage
.. |travis| image:: https://img.shields.io/travis/systori/systori/dev.svg
   :target: https://travis-ci.org/systori/systori
   :alt: Build
.. |python| image:: https://img.shields.io/badge/python-3.6-blue.svg
   :target: https://docs.python.org/3.6/index.html
   :alt: Python
.. |codestyle| image:: https://img.shields.io/badge/codestyle-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Codestyle
.. |chat| image:: https://img.shields.io/badge/chat-telegram-BBA892.svg
   :target: https://t.me/systori
   :alt: Chat
.. |style-check| image:: https://github.com/systori/systori/workflows/Style%20check/badge.svg
   :target: https://github.com/systori/systori/workflows/Style%20check/badge.svg
   :alt: Style check
