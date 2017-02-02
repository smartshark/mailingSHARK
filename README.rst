mailingSHARK
============
.. image:: https://travis-ci.org/smartshark/mailingSHARK.svg?branch=master
    :target: https://travis-ci.org/smartshark/mailingSHARK

mailingSHARK collects data from mailing list archives. Currently, pipermail is supported.

Documentation
-------------
https://smartshark.github.io/mailingSHARK/

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

=======
via Pip
=======
.. code-block:: bash

	$ sudo pip3 install https://github.com/smartshark/mailingSHARK/zipball/master --process-dependency-links

============
via setup.py
============
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

--help, -h: shows the help page for this command

--version, -v: shows the version

--db-user <USER>, -U <USER>: mongodb user name; Default: None

--db-password <PASSWORD>, -P <PASSWORD>: mongodb password; Default: None

--db-database <DATABASENAME>, -DB <DATABASENAME>: database name; Default: smartshark

--db-hostname <HOSTNAME>, -H <HOSTNAME>: hostname, where the mongodb runs on; Default: localhost

--db-port <PORT>, -p <PORT>: port, where the mongodb runs on; Default: 27017

--db-authentication <DB_AUTHENTICATION> -a <DB_AUTHENTICATION>: name of the authentication database; Default: None

--debug <DEBUG_LEVEL>, -d <DEBUG_LEVEL>: Debug level (INFO, DEBUG, WARNING, ERROR); Default: DEBUG

--project-name <PROJECT_NAME>: Name of the project, from which the data is collected; Required

--output -o <PATH>: Path to directory, where output can be stored (must be writable); Required

--mailingurl -m <URL>: Url of the mailing list archive; Required

--backend -b <BACKENDNAME>: Backend to use to download the emails; Required

--proxy-host <PROXYHOST>, -PH <PROXYHOST>: Proxy hostname or IP address; Default: None

--proxy-port <PROXYPORT>, -PP <PROXYPORT>: Port of the proxy to use; Default: None

--proxy-password <PROXYPASSWORD -Pp <PROXYPASSWORD>: Password to use the proxy (HTTP Basic Auth); Default: None

--proxy-user <PROXYUSER> -PU <PROXYUSER>: Username to use the proxy (HTTP Basic Auth); Default: None



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