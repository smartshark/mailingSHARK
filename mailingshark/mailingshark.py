import gzip
import logging
import os
import shutil
import timeit
import tarfile

import sys

from mongoengine import connect, DoesNotExist

from mailingshark.datacollection.basedatacollector import BaseDataCollector
from mailingshark.storage.models import Project
from mailingshark.analyzer import ParsedMessage
from email.parser import Parser
import codecs
import mailbox

logger = logging.getLogger("main")


class MailingSHARK(object):
    def __init__(self):
        pass

    def start(self, cfg):
        logger.setLevel(cfg.get_debug_level())
        start_time = timeit.default_timer()

        # Connect to mongodb
        connect(cfg.database, username=cfg.user, password=cfg.password, host=cfg.host,
                port=cfg.port, authentication_source=cfg.authentication_db)

        # Get the project for which issue data is collected
        try:
            project = Project.objects(url=cfg.project_url).get()
            if cfg.mailing_url not in project.mailing_urls:
                project.mailing_urls.append(cfg.mailing_url)
                project_id = project.save().id
            else:
                project_id = project.id
        except DoesNotExist:
            logger.error('Project not found. Use vcsSHARK beforehand!')
            sys.exit(1)

        # Find correct backend
        backend = BaseDataCollector.find_fitting_backend(cfg, project_id)
        logger.debug("Using backend: %s" % backend.identifier)

        # Get a list of all file paths to boxes
        found_files = backend.download_mail_boxes()
        logger.debug("Got the following files: %s" % found_files)

        # Unpack boxes (if necessary)
        boxes_to_analyze = self._unpack_files(found_files, cfg.temporary_dir)
        logger.info("Analyzing the following files: %s" % boxes_to_analyze)

        for path_to_box in boxes_to_analyze:
            box = mailbox.mbox(path_to_box, create=False)
            i = 0
            logger.debug("Analyzing: %s" % path_to_box)
            for msg in box:
                parsed_message = ParsedMessage(cfg, msg)

                '''
                print(msg.keys())
                print(msg.get('Message-ID'))
                if msg.get('References'):
                    print(msg.get('References').split("\n\t"))
                '''
                i += 1
            print(i)

        total_messages, stored_messages, non_parsed = (0, 0, 0)
        logger.info("%d messages analyzed" % total_messages)
        logger.info("%d messages stored in database %s" % (stored_messages, cfg.database))
        logger.info("%d messages ignored by the parser" % non_parsed)


        elapsed = timeit.default_timer() - start_time
        logger.info("Execution time: %0.5f s" % elapsed)

    def _unpack_files(self, file_paths, output_dir):
        for file_path in file_paths:
            if file_path.endswith('.tar.gz') or file_path.endswith('.tar'):
                opened_file = tarfile.open(file_path)
                opened_file.extractall(output_dir)

            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rb') as in_file:
                    s = in_file.read()

                # Now store the uncompressed data
                path_to_store = os.path.join(output_dir, os.path.basename(file_path)[:-3]+'.txt')  # remove the '.gz'

                # store uncompressed file data from 's' variable
                with open(path_to_store, 'wb') as f:
                    f.write(s)

            if file_path.endswith('.mbox'):
                shutil.move(file_path, os.path.join(output_dir, os.path.basename(file_path)))

        # Find all extracted files, which end with .txt or .mbox
        new_paths = []
        for root, directories, files in os.walk(output_dir):
            for filename in files:
                if filename.endswith('.txt') or filename.endswith('.mbox'):
                    # Join the two strings in order to form the full filepath.
                    file_path = os.path.join(root, filename)
                    new_paths.append(file_path)  # Add it to the list.

        return new_paths  # Self-explanatory.


