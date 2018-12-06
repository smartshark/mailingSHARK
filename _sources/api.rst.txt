=================
API Documentation
=================

Entry Point
===========
.. automodule:: main
    :members:
    :undoc-members:

Application
===========
.. autoclass:: mailingshark.mailingshark.MailingSHARK
   :members:

Configuration and Misc
======================

Configuration
-------------
.. autoclass:: mailingshark.config.Config
   :members:

.. autoclass:: mailingshark.config.ConfigValidationException
   :members:


Data Collectors
===============

BaseDataCollector
-----------------
.. autoclass:: mailingshark.datacollection.basedatacollector.BaseDataCollector
   :members:

Pipermail Collector
-------------------
.. autoclass:: mailingshark.datacollection.pipermail.PipermailBackend
   :members:


Utils
-----
.. automodule:: mailingshark.datacollection.common
   :members:


Models
------
.. autoclass:: mailingshark.analyzer.ParsedMessage
   :members:
