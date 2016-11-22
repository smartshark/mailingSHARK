import logging
import os
import shutil
from urllib.parse import urlparse

class ConfigValidationException(Exception):
    pass

class Config(object):
    def __init__(self, args):
        self.mailing_url = args.mailingurl.rstrip('/')
        self.backend = args.backend
        self.project_url = args.url.rstrip('/')
        self.host = args.db_hostname
        self.port = args.db_port
        self.user = args.db_user
        self.password = args.db_password
        self.database = args.db_database
        self.authentication_db = args.db_authentication
        self.mailing_user = args.mailing_user
        self.mailing_password = args.mailing_password
        self.debug = args.debug
        self.output_dir = args.output.rstrip('/')

        if args.proxy_host.startswith('http://'):
            self.proxy_host = args.proxy_host[7:]
        else:
            self.proxy_host = args.proxy_host

        self.proxy_port = args.proxy_port
        self.proxy_username = args.proxy_user
        self.proxy_password = args.proxy_password

        self.temporary_dir = os.path.join(self.output_dir, 'ready')

        self._validate_config()

    def get_mailing_url_identifier(self):
        parsed_url = urlparse(self.mailing_url)
        return parsed_url.netloc+'/'+parsed_url.path

    def _validate_config(self):
        if not os.path.exists(self.temporary_dir):
            os.makedirs(self.temporary_dir)
        else:
            shutil.rmtree(self.temporary_dir)
            os.makedirs(self.temporary_dir)

        if (self.mailing_user is not None and self.mailing_password is None) or \
                (self.mailing_password is not None and self.mailing_user is None):
            raise ConfigValidationException('Issue user and password must be set if either of them are not None.')

        if (self.proxy_username is not None and self.proxy_password is None) or \
                (self.proxy_password is not None and self.proxy_username is None):
            raise ConfigValidationException('Proxy user and password must be set if either of them are not None.')

    def get_debug_level(self):
        choices = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        return choices[self.debug]

    def _get_proxy_string(self):
        if self.proxy_password is None or self.proxy_username is None:
            return 'http://'+self.proxy_host+':'+self.proxy_port
        else:
            return 'http://'+self.proxy_username+':'+self.proxy_password+'@'+self.proxy_host+':'+self.proxy_port

    def get_proxy_dictionary(self):
        if self._use_proxy():
            proxies = {
                'http': self._get_proxy_string(),
                'https': self._get_proxy_string()
            }

            return proxies

        return None

    def _use_proxy(self):
        if self.proxy_host is None:
            return False

        return True

    def __str__(self):
        return "Config: identifier: %s, token: %s, mailing_url: %s, project_url: %s, host: %s, port: %s, user: %s, " \
               "password: %s, database: %s, authentication_db: %s, proxy_host: %s, proxy_port: %s, proxy_username: %s" \
               "proxy_password: %s, mailing_user: %s, mailing_password: %s" % \
               (
                   self.identifier,
                   self.token,
                   self.tracking_url,
                   self.project_url,
                   self.host,
                   self.port,
                   self.user,
                   self.password,
                   self.database,
                   self.authentication_db,
                   self.proxy_host,
                   self.proxy_port,
                   self.proxy_username,
                   self.proxy_password,
                   self.mailing_user,
                   self.mailing_password
               )



