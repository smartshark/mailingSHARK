import gzip
import logging
import os
import shutil
import timeit
import tarfile

import sys

import datetime
from mongoengine import connect, DoesNotExist

from mailingshark.datacollection.basedatacollector import BaseDataCollector
from mailingshark.analyzer import ParsedMessage
import mailbox

from mailingshark.mongomodels import MailingList, Project, Message, People

logger = logging.getLogger("main")


class MailingSHARK(object):
    def __init__(self):
        self.people = {}
        self.messages = {}

    def start(self, cfg):
        logger.setLevel(cfg.get_debug_level())
        start_time = timeit.default_timer()

        # Connect to mongodb
        connect(cfg.database, username=cfg.user, password=cfg.password, host=cfg.host,
                port=cfg.port, authentication_source=cfg.authentication_db)

        # Get the project for which issue data is collected
        try:
            project_id = Project.objects(name=cfg.project_name).get().id
        except DoesNotExist:
            logger.error('Project not found. Use vcsSHARK beforehand!')
            sys.exit(1)

        # Try to create the mailing_list in database
        try:
            mailing_list = MailingList.objects(project_id=project_id, name=cfg.mailing_url).get()
        except DoesNotExist:
            mailing_list = MailingList(project_id=project_id, name=cfg.mailing_url)
        mailing_list.last_updated = datetime.datetime.now()
        mailing_list_id = mailing_list.save().id

        # Find correct backend
        backend = BaseDataCollector.find_fitting_backend(cfg, project_id)
        logger.debug("Using backend: %s" % backend.identifier)

        # Get a list of all file paths to boxes
        found_files = backend.download_mail_boxes()
        logger.debug("Got the following files: %s" % found_files)

        # Unpack boxes (if necessary)
        boxes_to_analyze = self._unpack_files(found_files, cfg.temporary_dir)
        logger.info("Analyzing the following files: %s" % boxes_to_analyze)

        stored_messages, non_parsed = (0, 0)
        for path_to_box in boxes_to_analyze:
            box = mailbox.mbox(path_to_box, create=False)
            logger.info("Analyzing: %s" % path_to_box)
            for msg in box:
                parsed_message = ParsedMessage(cfg, msg)
                logger.debug('Got the following message: %s' % parsed_message)

                self.__store_message(parsed_message, mailing_list_id)
                stored_messages += 1

        logger.info("%d messages stored in database %s" % (stored_messages, cfg.database))
        logger.info("%d messages ignored by the parser" % non_parsed)

        elapsed = timeit.default_timer() - start_time
        logger.info("Execution time: %0.5f s" % elapsed)

    def __store_message(self, parsed_message, list_id):
        try:
            mongo_message = Message.objects(message_id=parsed_message.message_id, mailing_list_id=list_id).get()
        except DoesNotExist:
            mongo_message = Message(message_id=parsed_message.message_id, mailing_list_id=list_id)

        mongo_message.subject = parsed_message.subject
        mongo_message.body = parsed_message.body
        mongo_message.patches = parsed_message.patches
        mongo_message.date = parsed_message.date

        if parsed_message.in_reply_to and parsed_message.in_reply_to is not None:
            mongo_message.in_reply_to_id = self._get_message(parsed_message.in_reply_to, list_id)

        if parsed_message.references:
            reference_ids = []
            for reference in parsed_message.references:
                reference_ids.append(self._get_message(reference, list_id))
            mongo_message.reference_ids = reference_ids

        if getattr(parsed_message, 'from'):
            mongo_message.from_id = self._get_people(getattr(parsed_message, 'from')[0])

        if parsed_message.to:
            to_ids = []
            for user_to in parsed_message.to:
                to_ids.append(self._get_people(user_to))
            mongo_message.to_ids = to_ids

        if parsed_message.cc:
            cc_ids = []
            for user_cc in parsed_message.cc:
                cc_ids.append(self._get_people(user_cc))
            mongo_message.cc_ids = cc_ids

        # Save this call in a dictionary to save network traffic
        mongo_id = mongo_message.save().id
        self.messages[parsed_message.message_id] = mongo_id

    def _get_message(self, message_id, list_id):
        if message_id in self.messages:
            return self.messages[message_id]

        try:
            mongo_id = Message.objects(message_id=message_id, mailing_list_id=list_id).get().id
        except DoesNotExist:
            mongo_id = Message(message_id=message_id, mailing_list_id=list_id).save().id

        self.messages[message_id] = mongo_id
        return mongo_id

    def _get_people(self, user):

        # Username is the first part of the email address
        username = user[1].split('@')[0]
        email = user[1]
        name = user[0]

        # Check if user was accessed before. This reduces the amount of API requests
        if email in self.people:
            return self.people[email]

        # Replace the email address "anonymization"
        people_id = People.objects(name=name, email=email).upsert_one(name=name, email=email, username=username).id
        self.people[username] = people_id
        return people_id

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

            #if file_path.endswith('.mbox'):
            #    shutil.move(file_path, os.path.join(output_dir, os.path.basename(file_path)))

        # Find all extracted files, which end with .txt or .mbox
        new_paths = []
        for root, directories, files in os.walk(output_dir):
            for filename in files:
                if filename.endswith('.txt') or filename.endswith('.mbox'):
                    # Join the two strings in order to form the full filepath.
                    file_path = os.path.join(root, filename)
                    new_paths.append(file_path)  # Add it to the list.

        return new_paths  # Self-explanatory.


