import logging
import os
import shutil
import unittest
import gzip
from urllib.parse import urlparse

import mock
from bs4 import BeautifulSoup

from mailingshark.datacollection.pipermail import PipermailBackend


class ConfigMock(object):
    def __init__(self, mailing_url):
        self.debug_level = 'DEBUG'
        self.mailing_url = mailing_url
        self.output_dir = os.path.dirname(os.path.realpath(__file__))+'/testdata/out'

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

    def get_mailing_url_identifier(self):
        parsed_url = urlparse(self.mailing_url)
        return parsed_url.netloc + parsed_url.path


class PipermailBackendTest(unittest.TestCase):

    def setUp(self):
        # Setup logging
        logging.basicConfig(level=logging.ERROR)

        # Renew output folder
        shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/testdata/out', ignore_errors=True)
        os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '/testdata/out')

    @mock.patch('mailingshark.datacollection.pipermail.requests.get')
    def test_get_links_pipermail_archive(self, requests_get):
        # Fake data load
        with open(os.path.dirname(os.path.realpath(__file__))+'/testdata/mail-archive-pipermail.html', 'r') as html_file:
            html_data = html_file.read()

        requests_get.return_value.ok = True
        requests_get.return_value.text = html_data

        backend = PipermailBackend(ConfigMock("https://mail.kde.org/pipermail/k3b"), None)
        links = backend.get_links()
        links = [link for link in links]

        expected_links = [
            "https://mail.kde.org/pipermail/k3b/2010-February.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-March.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-April.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-May.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-June.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-July.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-August.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-October.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-November.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2010-December.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2011-January.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2011-February.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2011-April.txt.gz",
            "https://mail.kde.org/pipermail/k3b/2016-December.txt.gz"
        ]

        self.assertListEqual(expected_links, links)

    @mock.patch('mailingshark.datacollection.pipermail.requests.get')
    def test_get_links_mbox_archive(self, requests_get):
        # Fake data load
        with open(os.path.dirname(os.path.realpath(__file__)) + '/testdata/mail-archive-mod_mbox.html',
                  'r') as html_file:
            html_data = html_file.read()

        requests_get.return_value.ok = True
        requests_get.return_value.text = html_data

        backend = PipermailBackend(ConfigMock("http://mail-archives.apache.org/mod_mbox/logging-log4j-user"), None)
        links = backend.get_links()
        links = [link for link in links]

        expected_links = [
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200012.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200105.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200212.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200312.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200412.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200505.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/201601.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/201701.mbox",
            "http://mail-archives.apache.org/mod_mbox/logging-log4j-user/201702.mbox",
        ]

        self.assertListEqual(expected_links, links)

    @mock.patch('mailingshark.datacollection.pipermail.PipermailBackend.get_links')
    @mock.patch('mailingshark.datacollection.pipermail.requests.get')
    def test_download_mail_boxes_pipermail(self, requests_get, get_links):
        # Fake data load
        with open(os.path.dirname(os.path.realpath(__file__)) + '/testdata/2010-April.txt.gz', 'rb') as gz_file:
            gz_file_content = gz_file.read()

        requests_get.return_value.ok = True
        requests_get.return_value.content = gz_file_content

        # Fake links
        get_links.return_value = ['https://mail.kde.org/pipermail/k3b/2010-April.txt.gz']

        backend = PipermailBackend(ConfigMock("https://mail.kde.org/pipermail/k3b"), None)

        mailing_mock = mock.Mock()
        mailing_mock.last_updated = None
        backend.download_mail_boxes(mailing_mock)

        self.assertTrue(
            os.path.isfile(
                os.path.dirname(os.path.realpath(__file__))+'/testdata/out/mail.kde.org/pipermail/k3b/2010-April.txt.gz'
            )
        )

    @mock.patch('mailingshark.datacollection.pipermail.PipermailBackend.get_links')
    @mock.patch('mailingshark.datacollection.pipermail.requests.get')
    def test_download_mail_boxes_mbox(self, requests_get, get_links):
        # Fake data load
        with open(os.path.dirname(os.path.realpath(__file__)) + '/testdata/200012.mbox', 'rb') as mbox_file:
            mbox_file_content = mbox_file.read()

        requests_get.return_value.ok = True
        requests_get.return_value.content = mbox_file_content

        # Fake links
        get_links.return_value = ['http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200012.mbox']

        backend = PipermailBackend(ConfigMock("http://mail-archives.apache.org/mod_mbox/logging-log4j-user"), None)

        mailing_mock = mock.Mock()
        mailing_mock.last_updated = None
        backend.download_mail_boxes(mailing_mock)

        self.assertTrue(
            os.path.isfile(
                os.path.dirname(
                    os.path.realpath(__file__)) +
                '/testdata/out/mail-archives.apache.org/mod_mbox/logging-log4j-user/200012.mbox'
            )
        )

    def test_filter_links_mbox(self):
        # Realistic fake data
        mbox_links = [
             'http://mail-archives.apache.org/mod_mbox/', '?format=atom', '201702.mbox/thread', '201702.mbox/date',
             '201702.mbox/author', '201701.mbox/thread', '201701.mbox/date', '201701.mbox/author', '201601.mbox/thread',
             '201601.mbox/date', '201601.mbox/author', '200505.mbox/thread', '200505.mbox/date', '200505.mbox/author',
             '200412.mbox/thread', '200412.mbox/date', '200412.mbox/author', '200312.mbox/thread', '200312.mbox/date',
             '200312.mbox/author', '200212.mbox/thread', '200212.mbox/date', '200212.mbox/author', '200105.mbox/thread',
             '200105.mbox/date', '200105.mbox/author', '200012.mbox/thread', '200012.mbox/date', '200012.mbox/author'
        ]

        # Expected links
        expected_filtered_links_mobx = [
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200012.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200105.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200212.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200312.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200412.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/200505.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/201601.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/201701.mbox',
            'http://mail-archives.apache.org/mod_mbox/logging-log4j-user/201702.mbox',
        ]

        # We get the reversed link list from the method and need to put it back in order to use assertListEqual
        backend = PipermailBackend(ConfigMock("http://mail-archives.apache.org/mod_mbox/logging-log4j-user"), None)
        links = [link for link in backend._filter_links(mbox_links)]
        self.assertListEqual(links, expected_filtered_links_mobx)

    def test_filter_links_pipermail(self):
        pipermail_links = [
            'https://mail.kde.org/mailman/listinfo/k3b', '2016-December/thread.html', '2016-December/subject.html',
            '2016-December/author.html', '2016-December/date.html', '2016-December.txt.gz', '2011-April/thread.html',
            '2011-April/subject.html', '2011-April/author.html', '2011-April/date.html', '2011-April.txt.gz',
            '2011-February/thread.html', '2011-February/subject.html', '2011-February/author.html',
            '2011-February/date.html', '2011-February.txt.gz', '2011-January/thread.html', '2011-January/subject.html',
            '2011-January/author.html', '2011-January/date.html', '2011-January.txt.gz', '2010-December/thread.html',
            '2010-December/subject.html', '2010-December/author.html', '2010-December/date.html',
            '2010-December.txt.gz', '2010-November/thread.html', '2010-November/subject.html',
            '2010-November/author.html', '2010-November/date.html', '2010-November.txt.gz', '2010-October/thread.html',
            '2010-October/subject.html', '2010-October/author.html', '2010-October/date.html', '2010-October.txt.gz',
            '2010-August/thread.html', '2010-August/subject.html', '2010-August/author.html', '2010-August/date.html',
            '2010-August.txt.gz', '2010-July/thread.html', '2010-July/subject.html', '2010-July/author.html',
            '2010-July/date.html', '2010-July.txt.gz', '2010-June/thread.html', '2010-June/subject.html',
            '2010-June/author.html', '2010-June/date.html', '2010-June.txt.gz', '2010-May/thread.html',
            '2010-May/subject.html', '2010-May/author.html', '2010-May/date.html', '2010-May.txt.gz',
            '2010-April/thread.html', '2010-April/subject.html', '2010-April/author.html', '2010-April/date.html',
            '2010-April.txt.gz', '2010-March/thread.html', '2010-March/subject.html', '2010-March/author.html',
            '2010-March/date.html', '2010-March.txt.gz', '2010-February/thread.html', '2010-February/subject.html',
            '2010-February/author.html', '2010-February/date.html', '2010-February.txt.gz'
        ]

        # Expected links
        expected_filtered_links_pipermail = [
            'https://mail.kde.org/pipermail/k3b/2010-February.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-March.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-April.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-May.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-June.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-July.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-August.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-October.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-November.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2010-December.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2011-January.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2011-February.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2011-April.txt.gz',
            'https://mail.kde.org/pipermail/k3b/2016-December.txt.gz',
        ]

        backend = PipermailBackend(ConfigMock("https://mail.kde.org/pipermail/k3b"), None)
        links = [link for link in backend._filter_links(pipermail_links)]
        self.assertListEqual(links, expected_filtered_links_pipermail)