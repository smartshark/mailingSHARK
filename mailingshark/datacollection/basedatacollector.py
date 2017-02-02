import abc
import os
import sys
import logging


class BaseDataCollector(metaclass=abc.ABCMeta):
    """
    Base class for data collection backends
    """

    @abc.abstractproperty
    def identifier(self):
        """
        Identifier of the backend

        .. WARNING:: Must be unique among all backends
        """
        return

    def __init__(self, cfg, project_id):
        """
        Initializes the backend

        :param cfg: object of class :class:`mailingshark.config.Config` that holds all configuration options
        :param project_id: id of the project of class :class:`bson.objectid.ObjectId`, to which the mailing list belongs
        """
        self.config = cfg
        self.project_id = project_id
        self.debug_level = logging.DEBUG

        if self.config is not None:
            self.debug_level = self.config.get_debug_level()

    @abc.abstractmethod
    def download_mail_boxes(self, mailing_list):
        """
        Download all mail boxes from the website of the mailing list

        :param mailing_list: object of MailingList class (see: pycoshark library)
        """
        pass

    @staticmethod
    def _import_backends():
        """
        Method to import all backends in the datacollection folder
        """
        backend_files = [x[:-3] for x in os.listdir(os.path.dirname(os.path.realpath(__file__))) if x.endswith(".py")]
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        for backend in backend_files:
            __import__(backend)

    @staticmethod
    def find_fitting_backend(cfg, project_id):
        """
        Find the fitting backend based on the identifier

        :param cfg: object of class :class:`mailingshark.config.Config` that holds all configuration options
        :param project_id: id of the project of class :class:`bson.objectid.ObjectId`, to which the mailing list belongs
        """
        BaseDataCollector._import_backends()

        for sc in BaseDataCollector.__subclasses__():
            backend = sc(cfg, project_id)
            if backend.identifier == cfg.backend:
                return backend

        return None

    @staticmethod
    def get_all_possible_backend_options():
        """
        Method that returns all available backend options
        """
        BaseDataCollector._import_backends()

        choices = []
        for sc in BaseDataCollector.__subclasses__():
            backend = sc(None, None)
            choices.append(backend.identifier)
        return choices
