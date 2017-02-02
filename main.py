import os
import logging
import logging.config
import json
import sys
import argparse

from mailingshark.config import Config, ConfigValidationException
from mailingshark.datacollection.basedatacollector import BaseDataCollector
from mailingshark.mailingshark import MailingSHARK


def setup_logging(default_path=os.path.dirname(os.path.realpath(__file__))+"/loggerConfiguration.json",
                  default_level=logging.INFO):
        """
        Setup logging configuration

        :param default_path: path to the logger configuration
        :param default_level: defines the default logging level if configuration file is not found \
         (default:logging.INFO)
        """
        path = default_path
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)


def writable_dir(prospective_dir):
    """ Function that checks if a path is a directory, if it exists and if it is writable and only
    returns true if all these three are the case

    :param prospective_dir: path to the directory"""

    if prospective_dir is not None:
        if not os.path.isdir(prospective_dir):
            os.makedirs(prospective_dir, exist_ok=True)
        if os.access(prospective_dir, os.W_OK):
            return prospective_dir
        else:
            raise Exception("output:{0} is not a writable dir".format(prospective_dir))


def start():
    """
    Starts the application. First parses the different command line arguments and then it gives these to
    :class:`mailingshark.mailingshark.MailingSHARK`.
    """
    setup_logging()
    logger = logging.getLogger("main")
    logger.info("Starting mailingSHARK...")

    try:
        backend_choices = BaseDataCollector.get_all_possible_backend_options()
    except Exception as e:
        logger.exception("Failed to instantiate backend.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Collects information from mailing lists.')
    parser.add_argument('-U', '--db-user', help='Database user name', default=None)
    parser.add_argument('-P', '--db-password', help='Database user password', default=None)
    parser.add_argument('-DB', '--db-database', help='Database name', default='smartshark')
    parser.add_argument('-H', '--db-hostname', help='Name of the host, where the database server is running',
                        default='localhost')
    parser.add_argument('-o', '--output', help='Directory, which can be used as output.',
                        required=True, type=writable_dir)
    parser.add_argument('-p', '--db-port', help='Port, where the database server is listening', default=27017, type=int)
    parser.add_argument('-a', '--db-authentication', help='Name of the authentication database', default=None)
    parser.add_argument('-n', '--project-name', help='Name of the project.', required=True)
    parser.add_argument('-m', '--mailingurl', help='URL to the bugtracking system.', required=True)
    parser.add_argument('-b', '--backend', help='Backend to use for the mailing parsing', choices=backend_choices)
    parser.add_argument('-PH', '--proxy-host', help='Proxy hostname or IP address.', default=None)
    parser.add_argument('-PP', '--proxy-port', help='Port of the proxy to use.', default=None)
    parser.add_argument('-Pp', '--proxy-password', help='Password to use the proxy (HTTP Basic Auth)', default=None)
    parser.add_argument('-PU', '--proxy-user', help='Username to use the proxy (HTTP Basic Auth)', default=None)
    parser.add_argument('--debug', help='Sets the debug level.', default='DEBUG',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    try:
        args = parser.parse_args()
        cfg = Config(args)
    except ConfigValidationException as e:
        logger.error(e)
        sys.exit(1)

    mailingshark = MailingSHARK()
    mailingshark.start(cfg)

if __name__ == "__main__":
    start()
