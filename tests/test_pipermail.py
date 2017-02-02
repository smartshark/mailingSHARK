import logging
import unittest

from mailingshark.datacollection.pipermail import PipermailBackend


class ConfigMock(object):
    def __init__(self):
        self.debug_level = 'DEBUG'
        self.mailing_url = "https://mail.kde.org/pipermail/k3b/"

    def get_debug_level(self):
        choices = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        return choices[self.debug_level]

    def get_proxy_dictionary(self):
        return None


class PipermailBackendTest(unittest.TestCase):

    def setUp(self):
        # Setup logging
        logging.basicConfig(level=logging.ERROR)

    def test_get_links(self):
        backend = PipermailBackend(ConfigMock(), None)
        links = backend.get_links()

        # We can not check for length here, as new messages and links will be added
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-March.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-April.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-May.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-June.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-July.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-August.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-October.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-November.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2010-December.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-January.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-February.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-April.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-May.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-June.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-October.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-November.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2011-December.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2012-March.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2012-May.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2012-August.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2012-September.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2012-October.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2012-November.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2012-December.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2013-March.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2013-April.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2013-May.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2013-September.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2013-October.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2013-November.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2014-January.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2014-February.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2014-March.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2014-September.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2014-October.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2014-November.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2014-December.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-January.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-February.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-March.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-April.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-May.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-June.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-July.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-August.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-September.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-October.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-November.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2015-December.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-January.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-February.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-March.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-April.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-May.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-June.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-July.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-August.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-September.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-October.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-November.txt.gz", links)
        self.assertIn("https://mail.kde.org/pipermail/k3b/2016-December.txt.gz", links)
