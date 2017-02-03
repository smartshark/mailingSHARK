============
Introduction
============

This introduction will show how the requirements of **mailingSHARK** , how it is installed, tested, and executed. Furthermore,
a small tutorial in the end will show step by step, how to use this tool.

mailingSHARK is written in Python and is a tool to collect communication data from mailing list archives.
This includes messages, people, as well as references between messages. Currently, only pipermail archives
are supported (e.g., `k3b mailing list <https://mail.kde.org/pipermail/k3b/>`_ or
`log4j mailing list <http://mail-archives.apache.org/mod_mbox/logging-log4j-user/>`_

We use a vanilla Ubuntu 16.04 operating system as basis for the steps that we describe. If necessary, we give hints
on how to perform this step with a different operating system.


.. WARNING:: This software is still in development.


Model Documentation
===================
The documentation for the used database models can be found here: https://smartshark.github.io/pycoSHARK/api.html


.. _installation:

Installation
============
The installation process is straight forward. For a vanilla Ubuntu 16.04, we need to install the following packages:

.. code-block:: bash

	$ sudo apt-get install git python3-pip python3-cffi


Furthermore, you need a running MongoDB. The process of setting up a MongoDB is explained here:
https://docs.mongodb.com/manual/installation/



After these requirements are met, first clone the
**mailingSHARK** `repository <https://github.com/smartshark/mailingSHARK/>`_ repository to a folder you want. In the
following, we assume that you have cloned the repository to **~/mailingSHARK**. Afterwards,
the installation of **mailingSHARK** can be done in two different ways:

via Pip
-------
.. code-block:: bash

	$ sudo pip3 install https://github.com/smartshark/mailingSHARK/zipball/master --process-dependency-links

via setup.py
------------
.. code-block:: bash

	$ sudo python3.5 ~/mailingSHARK/setup.py install



.. NOTE::
	It is advisable to change the location, where the logs are written to.
	They can be changed in the **~/mailingSHARK/loggerConfiguration.json**. There are different file handlers defined.
	Just change the "filename"-attribute to a location of your wish.


Tests
=====
The tests of **mailingSHARK** can be executed by calling

	.. code-block:: bash

		$ python3.5 ~/mailingSHARK/setup.py test

The tests can be found in the folder "tests". 

.. WARNING:: The generated tests are not fully complete. They just test the basic functionality.


Execution
==========
In this chapter, we explain how you can execute **mailingSHARK**. Furthermore, the different execution parameters are
explained in detail.

1) Choose a web mail archive address (e.g., https://mail.kde.org/pipermail/k3b/)

2) Make sure that your MongoDB is running!

	.. code-block:: bash

		$ sudo systemctl status mongodb

3) Make sure that the project from which you collect data is already in the project collection of the MongoDB. If not,
you can add them by:

	.. code-block:: bash

		$ db.project.insert({"name": <PROJECT_NAME>})


4) Execute **mailingSHARK** by calling

	.. code-block:: bash

		$ python3.5 ~/mailingSHARK/main.py


**mailingSHARK** supports different commandline arguments:

.. option:: --help, -h

	shows the help page for this command

.. option:: --version, -v

	shows the version

.. option:: --db-user <USER>, -U <USER>

	Default: None

	mongodb user name

.. option:: --db-password <PASSWORD>, -P <PASSWORD>

	Default: None

	mongodb password

.. option:: --db-database <DATABASENAME>, -DB <DATABASENAME>

	Default: smartshark

	database name

.. option:: --db-hostname <HOSTNAME>, -H <HOSTNAME>

	Default: localhost

	hostname, where the mongodb runs on

.. option:: --db-port <PORT>, -p <PORT>

	Default: 27017

	port, where the mongodb runs on

.. option:: --db-authentication <DB_AUTHENTICATION> -a <DB_AUTHENTICATION>

	Default: None

	name of the authentication database

.. option:: --debug <DEBUG_LEVEL>, -d <DEBUG_LEVEL>

	Default: DEBUG

	Debug level (INFO, DEBUG, WARNING, ERROR)

.. option:: --project-name <PROJECT_NAME>

	Required

	Name of the project, from which the data is collected

.. option:: --output <PATH>, -o <PATH>

	Required

	Path to directory, where output can be stored (must be writable)

.. option:: --mailingurl <URL>, -m <URL>

	Required

	Url of the mailing list archive

.. option:: --backend  <BACKENDNAME>, -b <BACKENDNAME>

	Required

	Backend to use to download the emails

.. option:: --proxy-host <PROXYHOST>, -PH <PROXYHOST>

	Default: None

	Proxy hostname or IP address.

.. option:: --proxy-port <PROXYPORT>, -PP <PROXYPORT>

	Default: None

	Port of the proxy to use.

.. option:: --proxy-password <PROXYPASSWORD>, -Pp <PROXYPASSWORD>

	Default: None

	Password to use the proxy (HTTP Basic Auth)

.. option:: --proxy-user <PROXYUSER>, -PU <PROXYUSER>

	Default: None

	Username to use the proxy (HTTP Basic Auth)


Tutorial
========

In this section we show step-by-step how you can store the messages of the k3b mailinglist
https://mail.kde.org/pipermail/k3b/ in the MongoDB

1.	First, you need to have a mongodb running (version 3.2+).
How this can be achieved is explained here: https://docs.mongodb.org/manual/.

.. WARNING::
	Make sure, that you activated the authentication of mongodb
	(**mailingSHARK** also works without authentication, but with authentication it is much safer!).
	Hints how this can be achieved are given `here <https://docs.mongodb.org/manual/core/authentication/>`_.

2. Add k3b to the projects table in MongoDB.

	.. code-block:: bash

		$ mongo
		$ use smartshark
		$ db.project.insert({"name": "k3b"})

3. Install **mailingSHARK**. An explanation is given above.

3. Enter the **mailingSHARK** directory via

	.. code-block:: bash

		$ cd mailingSHARK

4. Test if everything works as expected

	.. code-block:: bash

		$ python3.5 main.py --help

	.. NOTE:: If you receive an error here, it is most likely, that the installation process failed.

5. Create an empty directory

	.. code-block:: bash

		$ mkdir ~/temp

5. Execute **mailingSHARK**:

	.. code-block:: bash

		$ cd ~/mailingSHARK
		$ python3.5 main.py --backend pipermail --project-name k3b --mailingurl https://mail.kde.org/pipermail/k3b --output ~/temp


Thats it. The results are explained in the database documentation
of `SmartSHARK <http://smartshark2.informatik.uni-goettingen.de/documentation/>`_.


