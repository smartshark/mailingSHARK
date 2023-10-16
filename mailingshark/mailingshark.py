import gzip
import logging
import os
import shutil
import timeit
import tarfile

import sys

import datetime

from mongoengine import connect, DoesNotExist, ConnectionFailure

from mailingshark.datacollection.basedatacollector import BaseDataCollector
from mailingshark.analyzer import ParsedMessage
import mailbox

from pycoshark.mongomodels import MailingSystem, Project, Message, People
from pycoshark.utils import create_mongodb_uri_string
from deepdiff import DeepDiff

logger = logging.getLogger("main")


class MailingSHARK(object):
    """
    Main application class. Contains the most important process logic.
    The main application consists of different steps: \n

    1. Connects to MongoDB

    2. Finds the project, to which the mailing list belongs

    3. Generates a new mailing list entry, if not existent

    4. Finds the correct backend via
    :func:`mailingshark.datacollection.basedatacollector.BaseDataCollector.find_fitting_backend`

    5. Downloads the mailboxes using the backend
    (:func:`mailingshark.datacollection.basedatacollector.BaseDataCollector.download_mail_boxes`)

    6. Unpacks the files (if necessary) via :func:`mailingshark.mailingshark.MailingSHARK._unpack_files`

    7. Parses the messages, by created :class:`mailingshark.analyzer.ParsedMessage` objects

    8. Stores the messages, by calling :func:`mailingshark.mailingshark.MailingSHARK._store_message`


    """

    def __init__(self):
        """
        Initializes the people and messages directory, which are used in
        :func:`mailingshark.mailingshark.MailingSHARK._get_people` and
        :func:`mailingshark.mailingshark.MailingSHARK._get_message` to save traffic
        """
        self.people = {}
        self.messages = {}

    def start(self, cfg):
        """
        Starts the program

        :param cfg: configuration of class :class:`mailingshark.config.Config`
        """
        logger.setLevel(cfg.get_debug_level())
        start_time = timeit.default_timer()

        # Connect to mongodb
        uri = create_mongodb_uri_string(cfg.user, cfg.password, cfg.host, cfg.port, cfg.authentication_db,
                                        cfg.ssl_enabled)

        try:
            connect(cfg.database, host=uri)
        except ConnectionFailure:
            logger.error("Failed to connect to MongoDB")

        # Get the project for which issue data is collected
        try:
            project_id = Project.objects(name=cfg.project_name).get().id
        except DoesNotExist:
            logger.error('Project not found. Use vcsSHARK beforehand!')
            sys.exit(1)

        last_mailing_systems = MailingSystem.objects.filter(url=cfg.mailing_url).order_by('-collection_date').first()
        last_mailing_system_id = last_mailing_systems.id if last_mailing_systems else None

        mailing_list = MailingSystem(project_id=project_id, url=cfg.mailing_url, collection_date=datetime.datetime.now())

        mailing_system_id = mailing_list.save().id

        # Find correct backend
        backend = BaseDataCollector.find_fitting_backend(cfg, project_id)
        logger.debug("Using backend: %s" % backend.identifier)

        # Get a list of all file paths to boxes
        found_files = backend.download_mail_boxes(mailing_list)
        logger.debug("Got the following files: %s" % found_files)

        # Unpack boxes (if necessary)
        boxes_to_analyze = self._unpack_files(found_files, cfg.temporary_dir)
        logger.info("Analyzing the following files: %s" % boxes_to_analyze)

        stored_messages, non_stored = (0, 0)
        for path_to_box in boxes_to_analyze:
            box = mailbox.mbox(path_to_box, create=False)
            logger.info("Analyzing: %s" % path_to_box)
            for i in range(0, len(box)):
                try:
                    parsed_message = ParsedMessage(cfg, box.get(i))
                    logger.debug('Got the following message: %s' % parsed_message)
                    self._store_message(parsed_message, last_mailing_system_id, mailing_system_id)
                    stored_messages += 1
                except Exception as e:
                    logger.error("Could not parse message. Error: %s" % e)
                    non_stored += 1

        logger.info("%d messages stored in database %s" % (stored_messages, cfg.database))
        logger.info("%d messages ignored by the parser" % non_stored)

        elapsed = timeit.default_timer() - start_time
        logger.info("Execution time: %0.5f s" % elapsed)

    def _store_message(self, parsed_message, last_mailing_system_id, mailing_system_id):
        """
        Store or update a parsed message in the database.

        :param parsed_message: An instance of the :class:`mailingshark.analyzer.ParsedMessage` class.
        :param last_mailing_system_id: The object ID of the last mailing system.
        :param mailing_system_id: The object ID of the current mailing system.

        """

        # Get the message, if it exist in the database
        try:
            mongo_message = Message.objects.get(message_id=parsed_message.message_id, mailing_system_ids=last_mailing_system_id)
        except DoesNotExist:
            mongo_message = None
        try:
            new_message = Message.objects.get(message_id=parsed_message.message_id, mailing_system_ids=mailing_system_id)
        except DoesNotExist:
            new_message = Message(message_id=parsed_message.message_id, mailing_system_ids=[mailing_system_id])

        # Set all values
        new_message.subject = parsed_message.subject
        new_message.body = parsed_message.body
        new_message.patches = parsed_message.patches
        new_message.date = parsed_message.date

        if parsed_message.in_reply_to and parsed_message.in_reply_to is not None:
            new_message.in_reply_to_id = self._get_message(parsed_message.in_reply_to, last_mailing_system_id, mailing_system_id)

        if parsed_message.references:
            reference_ids = []
            for reference in parsed_message.references:
                reference_ids.append(self._get_message(reference, last_mailing_system_id, mailing_system_id))
            new_message.reference_ids = reference_ids

        if getattr(parsed_message, 'from'):
            new_message.from_id = self._get_people(getattr(parsed_message, 'from')[0])

        if parsed_message.to:
            to_ids = []
            for user_to in parsed_message.to:
                to_ids.append(self._get_people(user_to))
            new_message.to_ids = to_ids

        if parsed_message.cc:
            cc_ids = []
            for user_cc in parsed_message.cc:
                cc_ids.append(self._get_people(user_cc))
            new_message.cc_ids = cc_ids

        if mongo_message is not None:
            diff = DeepDiff(t1=mongo_message.__dict__, t2=new_message.__dict__, exclude_paths='mailing_system_ids')
            if diff:
                mongo_id = new_message.save().id
            else:
                if mailing_system_id not in mongo_message.mailing_system_ids:
                    mongo_message.mailing_system_ids.append(mailing_system_id)
                mongo_id = mongo_message.save().id
        else:
            mongo_id = new_message.save().id

        # Save this call in a dictionary to save network traffic, if there is a reply to this message
        self.messages[parsed_message.message_id] = mongo_id

    def _get_message(self, message_id, last_mailing_system_id, mailing_system_id):
        """
        Retrieve a message by its unique identifier from the database or cache.

        :param message_id: A string that uniquely identifies the message, typically in the format specified by
                          Message-ID (e.g., https://en.wikipedia.org/wiki/Message-ID).
        :param last_mailing_system_id: The object ID of the last mailing system to which the message belonged, of class
                                      :class:`bson.objectid.ObjectId`.
        :param mailing_system_id: The object ID of the current mailing system to which the message belongs, of class
                                 :class:`bson.objectid.ObjectId`.
        """
        if message_id in self.messages:
            return self.messages[message_id]

        try:
            message = Message.objects(message_id=message_id, mailing_system_ids=last_mailing_system_id).get()
            if mailing_system_id not in message.mailing_system_ids:
                message.mailing_system_ids.append(mailing_system_id)
            mongo_id = message.save().id
        except DoesNotExist:
            mongo_id = None
        if not mongo_id:
            try:
                mongo_id = Message.objects(message_id=message_id, mailing_system_ids=mailing_system_id).get().id
            except DoesNotExist:
                mongo_id = Message(message_id=message_id, mailing_system_ids=[mailing_system_id]).save().id

        self.messages[message_id] = mongo_id
        return mongo_id

    def _get_people(self, user):
        """
        Gets the correct user from the people collection. Looks up the user in the people dictionary first to
        save network traffic.

        :param user: list, where the first part is the name and the second part is the email address
        """

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
        """
        Unpacks the files if they are .gz or .tar.gz or .tar files (based on the files paths in file_paths) and
        stores the contents in the output_dir.

        :param file_paths: paths of files that were downloaded (list)
        :param output_dir: path to directory were the output is saved
        """
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

            if file_path.endswith('.mbox') or file_path.endswith('.txt'):
                print(file_path)
                shutil.move(file_path, os.path.join(output_dir, os.path.basename(file_path)))

        # Find all extracted files, which end with .txt or .mbox
        new_paths = []
        for root, directories, files in os.walk(output_dir):
            for filename in files:
                if filename.endswith('.txt') or filename.endswith('.mbox'):
                    # Join the two strings in order to form the full filepath.
                    file_path = os.path.join(root, filename)
                    new_paths.append(file_path)  # Add it to the list.

        return new_paths


