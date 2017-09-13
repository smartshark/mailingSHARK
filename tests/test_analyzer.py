import logging
import mailbox
import unittest
import os

import datetime

from mailingshark.analyzer import ParsedMessage


class ConfigMock(object):
    def __init__(self):
        self.debug_level = 'DEBUG'

    def get_debug_level(self):
        choices = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        return choices[self.debug_level]


class ParseMessageTest(unittest.TestCase):

    def setUp(self):
        # Setup logging
        logging.basicConfig(level=logging.ERROR)

    def test_analyze_mbox_erronous_date(self):
        messages = mailbox.mbox(os.path.dirname(os.path.realpath(__file__)) + '/testdata/200307_xalanj.mbox', create=False)
        parsed_messages = []
        for msg in messages:
            parsed_messages.append(ParsedMessage(ConfigMock(), msg))

        self.assertEqual(126, len(parsed_messages))

    def test_analyze_txt(self):
        april2010 = mailbox.mbox(os.path.dirname(os.path.realpath(__file__))+'/testdata/2010-April.txt', create=False)
        parsed_messages = []
        for msg in april2010:
            parsed_messages.append(ParsedMessage(ConfigMock(), msg))

        self.assertEqual(14, len(parsed_messages))

        # Check message 1
        msg = parsed_messages[0]
        self.assertEqual("<4BBB2382.8040005@gmail.com>", msg.message_id)
        self.assertEqual("Hello,\n\non a machine with debian squeeze and k3b 1.90.0~rc1 i have hal running, \n"
                         "but is not finding devices (parallel ata dvd burner). It was upgraded "
                         "\nfrom k3b 1.x which was working beautifully. I've found the same issue in "
                         "\nthe gentoo bug here:\n"
                         "\nhttp://bugs.gentoo.org/292281\n"
                         "\nIn the bug it is suggested to use policykit instead of hal as backend. \n"
                         "Would you reccomend that too as safer choice for a distribution?\n"
                         "\nthanks,"
                         "\nriccardo\n\n", msg.body)
        self.assertEqual(None, msg.patches)
        self.assertEqual("[k3b] k3b hal backend not finding devices", msg.subject)
        self.assertEqual(datetime.datetime(2010,4,6,14,5,22), msg.date)
        self.assertEqual(7200, msg.date_tz)
        self.assertEqual([('Riccardo Magliocchetti', 'riccardo.magliocchetti@gmail.com')], getattr(msg, 'from'))
        self.assertEqual(None, msg.to)
        self.assertEqual(None, msg.cc)
        self.assertEqual(None, msg.in_reply_to)
        self.assertEqual([], msg.references)

        # Check message 2
        msg = parsed_messages[1]
        self.maxDiff = None
        self.assertEqual("<201004061547.18196.kamikazow@web.de>", msg.message_id)
        self.assertEqual("Am Dienstag 06 April 2010 14:05:22 schrieb Riccardo Magliocchetti:\n"
                         "> In the bug it is suggested to use policykit instead of hal as backend.\n"
                         "> Would you reccomend that too as safer choice for a distribution?\n\n"
                         "I've read roughly through the bug report and frankly I don't get it.\n"
                         "HAL is an abstraction layer for hardware (hence its name) and PolicyKit is \n"
                         "used for user authentication which K3b already uses through KAuth\n\n", msg.body)
        self.assertEqual(None, msg.patches)
        self.assertEqual("[k3b] k3b hal backend not finding devices", msg.subject)
        self.assertEqual(datetime.datetime(2010, 4, 6, 15, 47, 17), msg.date)
        self.assertEqual(7200, msg.date_tz)
        self.assertEqual([('Markus', 'kamikazow@web.de')], getattr(msg, 'from'))
        self.assertEqual(None, msg.to)
        self.assertEqual(None, msg.cc)
        self.assertEqual("<4BBB2382.8040005@gmail.com>", msg.in_reply_to)
        self.assertEqual(["<4BBB2382.8040005@gmail.com>"], msg.references)


    def test_analyze_mbox(self):
        april2010 = mailbox.mbox(os.path.dirname(os.path.realpath(__file__)) + '/testdata/200012.mbox', create=False)
        parsed_messages = []
        for msg in april2010:
            parsed_messages.append(ParsedMessage(ConfigMock(), msg))

        self.assertEqual(50, len(parsed_messages))

        # Check message 2
        msg = parsed_messages[1]
        self.assertEqual("<B65DE3DB.67BF%pier@betaversion.org>", msg.message_id)
        self.assertEqual("Let's try it again with the reply-to set (hopefully) correctly...\n\n    Pier\n\n-- \n"+
                         "Pier Fumagalli  <http://www.betaversion.org/>  <mailto:pier@betaversion.org>\n"+
                         "----------------------------------------------------------------------------\n\n\n", msg.body)
        self.assertEqual(None, msg.patches)
        self.assertEqual("The previous test didn't work correctly...", msg.subject)
        self.assertEqual(datetime.datetime(2000, 12, 14, 2, 41, 31), msg.date)
        self.assertEqual(-28800, msg.date_tz)
        self.assertEqual([('Pier P. Fumagalli', 'pier@betaversion.org')], getattr(msg, 'from'))
        self.assertEqual([('log4j-cvs', 'log4j-cvs@jakarta.apache.org'), ('log4j-dev', 'log4j-dev@jakarta.apache.org'),
                          ('log4j-user', 'log4j-user@jakarta.apache.org')], msg.to)
        self.assertEqual(None, msg.cc)
        self.assertEqual(None, msg.in_reply_to)
        self.assertEqual([], msg.references)

        # Check message 3
        msg = parsed_messages[2]
        self.assertEqual("<B65DE478.67C3%pier@betaversion.org>", msg.message_id)
        self.assertEqual("(I hate EZMLM!) :)\n\n    Pier\n\n-- \n" +
                         "Pier Fumagalli  <http://www.betaversion.org/>  <mailto:pier@betaversion.org>\n" +
                         "----------------------------------------------------------------------------\n\n\n", msg.body)
        self.assertEqual(None, msg.patches)
        self.assertEqual("Hopefully this should be right...", msg.subject)
        self.assertEqual(datetime.datetime(2000, 12, 14, 2, 44, 8), msg.date)
        self.assertEqual(-28800, msg.date_tz)
        self.assertEqual([('Pier P. Fumagalli', 'pier@betaversion.org')], getattr(msg, 'from'))
        self.assertEqual([('log4j-cvs', 'log4j-cvs@jakarta.apache.org'), ('log4j-dev', 'log4j-dev@jakarta.apache.org'),
                          ('log4j-user', 'log4j-user@jakarta.apache.org')], msg.to)
        self.assertEqual(None, msg.cc)
        self.assertEqual(None, msg.in_reply_to)
        self.assertEqual([], msg.references)

        # Check message 4
        msg = parsed_messages[3]
        self.assertEqual("<5.0.0.25.0.20001214150902.00aefaa0@mail.urbanet.ch>", msg.message_id)
        self.assertEqual("\nHi Guy,\n\nIt's not public yet but since you have asked: yes, log4j should become a \n"
                         "jakarta project in the next few days.\n\n"
                         "There are now two new mailing lists: log4j-dev@jakarta.apache.org and \n"
                         "log4j-user@jakarta.apache.org which replace the old log4j-dev@log4j.org and \n"
                         "log4j-public@log4j.org mailing lists. The members of the old lists have \n"
                         "been automatically subscribed to the corresponding list on \n"
                         "jakarta.apache.org. The CVS repository has also moved to Apache.\n\n"
                         "There is a strong push to rename the package to \"org.apache.log4j\". I have \n"
                         "already committed to do this for the next major log4j release scheduled for \n"
                         "1Q 2001. If you have a good reason to oppose a name change, then let us \n"
                         "know so that we can raise the issue with the apache group.  This is your \n"
                         "chance to speak up.\n\n"
                         "Some Apache members have suggested abandoning the name \"log4j\" altogether. \n"
                         "I personally don't have a problem with that since I don't really like the \n"
                         "name log4j. I have proposed the name \"cat\" (for cat-egory) or equivalently \n"
                         "jakarta-cat. The package hierarchy would start at \"org.apache.cat.\" Other \n"
                         "names/proposals are most welcome. Ceki\n\n\n\n"
                         "At 15:36 14.12.2000 +0200, Guy Nirpaz wrote:\n"
                         ">Hi,\n"
                         ">\n"
                         ">I was wondering, is Log4j going into Jakarta? If so, when?\n"
                         ">\n"
                         ">Thanks,\n"
                         ">\n"
                         ">Guy Nirpaz\n"
                         ">Java Architect\n"
                         ">\n"
                         ">Tantian Corp.\n"
                         ">guyn@tantian.com\n"
                         ">\n"
                         ">_______________________________________________\n"
                         ">log4j-dev mailing list\n"
                         ">log4j-dev@log4j.org\n"
                         ">http://lists.sourceforge.net/mailman/listinfo/log4j-dev\n", msg.body)
        self.assertEqual([], msg.patches)
        self.assertEqual("Re: Is Log4j getting into Jakarta?", msg.subject)
        self.assertEqual(datetime.datetime(2000, 12, 14, 15, 38, 59), msg.date)
        self.assertEqual(3600, msg.date_tz)
        self.assertEqual([('Ceki Gulcu', 'cgu@urbanet.ch')], getattr(msg, 'from'))
        self.assertEqual([('Guy Nirpaz', 'guyn@tantian.com')], msg.to)
        self.assertEqual([('log4j-dev', 'log4j-dev@jakarta.apache.org'), ('log4j-user', 'log4j-user@jakarta.apache.org')], msg.cc)
        self.assertEqual("<006e01c065d2$e316e580$0100000a@tantian.local>", msg.in_reply_to)
        self.assertEqual([], msg.references)