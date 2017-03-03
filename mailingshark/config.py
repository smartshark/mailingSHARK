import logging
import os
import shutil
from urllib.parse import urlparse


class ConfigValidationException(Exception):
    """
    Exception that is thrown if the configuration validation fails
    """
    pass


class Config(object):
    """
    Holds configuration information
    """
    def __init__(self, args):
        """
        Initializes the object via arguments from the argumentparser

        :param args: argumentparser of the class :class:`argparse.ArgumentParser`
        """
        self.mailing_url = args.mailingurl.rstrip('/')
        self.backend = args.backend
        self.project_name = args.project_name
        self.host = args.db_hostname
        self.port = args.db_port
        self.user = args.db_user
        self.password = args.db_password
        self.database = args.db_database
        self.authentication_db = args.db_authentication
        self.debug = args.debug
        self.output_dir = args.output.rstrip('/')

        if args.proxy_host is not None and args.proxy_host.startswith('http://'):
            self.proxy_host = args.proxy_host[7:]
        else:
            self.proxy_host = args.proxy_host

        self.proxy_port = args.proxy_port
        self.proxy_username = args.proxy_user
        self.proxy_password = args.proxy_password
        self.ssl_enabled = args.ssl

        self.temporary_dir = os.path.join(self.output_dir, 'ready')
        self._validate_config()

    def get_mailing_url_identifier(self):
        """
        Gets the mailing list url identifier
        """
        parsed_url = urlparse(self.mailing_url)
        return parsed_url.netloc+parsed_url.path

    def _validate_config(self):
        """
        Validates the config: the temporary dir must exist and if a proxy username is given, there must be a proxy
        password and vice versa
        """
        if not os.path.exists(self.temporary_dir):
            os.makedirs(self.temporary_dir)
        else:
            shutil.rmtree(self.temporary_dir)
            os.makedirs(self.temporary_dir)

        if (self.proxy_username is not None and self.proxy_password is None) or \
                (self.proxy_password is not None and self.proxy_username is None):
            raise ConfigValidationException('Proxy user and password must be set if either of them are not None.')

    def get_debug_level(self):
        """
        Gets the correct debug level, based on :mod:`logging`
        """
        choices = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        return choices[self.debug]

    def _get_proxy_string(self):
        """
        Gets the proxy string to do the requests
        """
        if self.proxy_password is None or self.proxy_username is None:
            return 'http://'+self.proxy_host+':'+self.proxy_port
        else:
            return 'http://'+self.proxy_username+':'+self.proxy_password+'@'+self.proxy_host+':'+self.proxy_port

    def get_proxy_dictionary(self):
        """
        Creates the proxy directory for the requests
        """
        if self._use_proxy():
            proxies = {
                'http': self._get_proxy_string(),
                'https': self._get_proxy_string()
            }

            return proxies

        return None

    def _use_proxy(self):
        """
        Checks if a proxy is used
        """
        if self.proxy_host is None:
            return False

        return True

    def __str__(self):
        return "Config: mailing_url: %s, project_name: %s, host: %s, port: %s, user: %s, " \
               "password: %s, database: %s, authentication_db: %s, proxy_host: %s, proxy_port: %s, proxy_username: %s" \
               "proxy_password: %s" % \
               (
                   self.mailing_url,
                   self.project_name,
                   self.host,
                   self.port,
                   self.user,
                   self.password,
                   self.database,
                   self.authentication_db,
                   self.proxy_host,
                   self.proxy_port,
                   self.proxy_username,
                   self.proxy_password
               )



