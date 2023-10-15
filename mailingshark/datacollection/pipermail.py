import logging

import requests
import os
from bs4 import BeautifulSoup

from mailingshark.datacollection.common import find_month_were_mailing_list_was_last_parsed
from mailingshark.datacollection.basedatacollector import BaseDataCollector


logger = logging.getLogger('backend')

COMPRESSED_TYPES = ['.gz', '.bz2', '.zip', '.tar',
                    '.tar.gz', '.tar.bz2', '.tgz', '.tbz']
ACCEPTED_TYPES = ['.mbox', '.txt']
MOD_MBOX_THREAD_STR = "/thread"


class PipermailBackend(BaseDataCollector):
    """
    Backend to download emails from pipermail archives
    """

    @property
    def identifier(self):
        """
        Identifier of the backend (pipermail)
        """
        return 'pipermail'

    def __init__(self, cfg, project_id):
        """
        See: :class:`mailingshark.datacollection.basedatacollector.BaseDataCollector`

        :param cfg: object of class :class:`mailingshark.config.Config` that holds all configuration options
        :param project_id: id of the project of class :class:`bson.objectid.ObjectId`, to which the mailing list belongs
        """
        super().__init__(cfg, project_id)

        logger.setLevel(self.debug_level)

    def download_mail_boxes(self, mailing_list):
        """
        See: :func:`mailingshark.datacollection.basedatacollector.BaseDataCollector.download_mail_boxes`

        :param mailing_list: object of MailingList class (see: pycoshark library)
        """
        base_path = os.path.join(self.config.output_dir, self.config.get_mailing_url_identifier())
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        links = self.get_links()
        logger.debug("Got links %s" % links)

        paths = []
        for link in links:
            logger.debug("Trying link: %s" % link)

            # We get the last part of the link as file name
            path = os.path.join(base_path, link.split('/')[-1])

            paths.append(path)
            if not os.path.isfile(path):
                logger.info('Downloading %s...' % link)
                response = requests.get(link, proxies=self.config.get_proxy_dictionary())
                with open(path, 'wb') as target_file:
                    target_file.write(response.content)
            else:
                logger.info('Already got %s...' % link)

        return paths

    def get_links(self):
        """
        Gets the links to all maling list boxes or archives by parsing the html site
        """
        req = requests.get(self.config.mailing_url, proxies=self.config.get_proxy_dictionary())

        if req.status_code != 200:
            logger.error('Could not access url %s' % self.config.mailing_url)

        # Parse html and fill link list
        soup = BeautifulSoup(req.text, 'html.parser')
        links = []
        for link in soup.findAll('a'):
            links.append(link.get('href'))

        return self._filter_links(links)

    def _filter_links(self, links):
        """
        Filter according to file types found in the archive index.

        :param links: list of all found links
        """
        accepted_types = COMPRESSED_TYPES + ACCEPTED_TYPES

        filtered_links = []
        for l in links:
            # Links from Apache's 'mod_mbox' plugin contain
            # trailing "/thread" substrings. Remove them to get
            # the links where mbox files are stored.
            if l.endswith(MOD_MBOX_THREAD_STR):
                l = l[:-len(MOD_MBOX_THREAD_STR)]

            ext1 = os.path.splitext(l)[-1]
            ext2 = os.path.splitext(l.rstrip(ext1))[-1]

            # Ignore links with not recognized extension
            if ext1 in accepted_types or ext1+ext2 in accepted_types:
                filtered_links.append(os.path.join(self.config.mailing_url, l))

        return reversed(filtered_links)
