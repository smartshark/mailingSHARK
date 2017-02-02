How to Extend
=============
**mailingSHARK** can be extended by adding new data collection backends from which emails can be downloaded.

All backends are stored in the mailingshark/datacollection folder. There are conditions, which must be fulfilled by the
backends so that it is accepted by the **mailingSHARK**:

1. The \*.py file for this backend must be stored in the mailingshark/datacollection folder.
2. It must inherit from :class:`~mailingshark.datacollection.basedatacollector.BaseDataCollector`
and implement the methods defined there.

The process of chosing the backend is the following:

*	Every backend gets instantiated

*	If the by the user choosen backend identifier matches the :func:`~mailingshark.datacollection.basedatacollector.BaseDataCollector.identifier` it is chosen

There are several important things to note:

1.	If you want to use a logger for your implementation, get it via

	.. code-block:: python

		logger = logging.getLogger("backend")


2.	The execution logic is in the application class and explained here :class:`~pyvcsshark.Application`.

3. If you want to have an example how to implement this class, look at
:class:`~mailingshark.datacollection.pipermail.PipermailBackend`

