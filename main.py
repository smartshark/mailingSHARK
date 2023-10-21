import os
import logging
import logging.config
import json
import sys
import argparse

from mailingshark.config import Config, ConfigValidationException
from mailingshark.datacollection.basedatacollector import BaseDataCollector
from mailingshark.mailingshark import MailingSHARK
from pycoshark.utils import get_base_argparser, delete_last_system_data_on_failure


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

    parser = get_base_argparser('Collects information from mailing lists.', '1.0.0')
    parser.add_argument('-o', '--output', help='Directory, which can be used as output.',
                        required=True, type=writable_dir)
    parser.add_argument('-n', '--project-name', help='Name of the project.', required=True)
    parser.add_argument('-m', '--mailing-url', help='URL to the bugtracking system.', required=True)
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
    try:
        mailingshark.start(cfg)
    except (KeyboardInterrupt, Exception) as e:
        logger.error(f"Program did not run successfully. Reason:{e}")
        logger.info(f"Deleting uncompleted data .....")
        delete_last_system_data_on_failure('mailing_system', cfg.mailing_url, db_user=cfg.user, db_password=cfg.password,
                                      db_hostname= cfg.host, db_port=cfg.port, db_authentication_db=cfg.authentication_db,
                                      db_ssl=cfg.ssl_enabled, db_name=cfg.database)

if __name__ == "__main__":
    start()
