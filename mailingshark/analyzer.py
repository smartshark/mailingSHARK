"""
The logic in this class is related to the project "MailingListStats" of MetricsGrimoire (see: analyzer.py)
"""
import codecs
import hashlib
import logging
import re
import datetime
from email.header import decode_header
from email.iterators import typed_subpart_iterator

from email.utils import parsedate_tz, getaddresses

logger = logging.getLogger("analyzer")

EMAIL_OBFUSCATION_PATTERNS = [' at ', '_at_', ' en ']


def to_unicode(text, charset):
    if charset is None:
        charset = 'latin-1'

    # In python3 strings are unicode by default
    if isinstance(text, str):
        return text
    elif isinstance(text, bytes):
        for encoding in [charset, 'ascii', 'utf-8', 'iso-8859-15']:
            try:
                return text.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        else:
            # All conversions failed, get unicode with unknown characters
            return codecs.decode(text, errors='replace')
    else:
        raise TypeError('string should be of str type')


class ParsedMessage(object):
    """
    Model to which the raw message is given that turns it into a parsed message
    """

    def __init__(self, cfg, raw_message):
        """
        Creates the parsed message using config cfg and message raw_message

        :param cfg: object of class :class:`mailingshark.config.Config`
        :param raw_message: object of class :class:`email.message.Message`
        """
        logger.setLevel(cfg.get_debug_level())

        # Clean up reply_noise
        re_reply_to = re.compile('^.*[^<]*(<.*>).*', re.IGNORECASE)
        charset = raw_message.get_content_charset()

        # Set attributes
        self.msgdate = self.__set_msgdate(raw_message)

        # The 'body' is not actually part of the header, but it will be
        # treated as any other header
        self.body, self.patches = self.__get_body(raw_message, charset)
        self.subject = self.__decode(raw_message.get('subject'), charset)

        self.__set_addresses(raw_message, charset)
        self.date, self.date_tz = self.__get_date(raw_message)

        if raw_message.get('in-reply-to') and raw_message.get('in-reply-to') is not None:
            self.in_reply_to = re_reply_to.sub(r'\1', self.__decode(raw_message.get('in-reply-to'), charset))
        else:
            self.in_reply_to = None

        # set message-id
        self.message_id = self.__create_message_id(raw_message)

        # set references
        if not isinstance(raw_message.get('references'), str) and not isinstance(raw_message.get('refernces'), bytes) \
                and raw_message.get('references') is not None:
            logger.warning('Reference header is not a string')
            self.references = []
            return

        if raw_message.get('references') and raw_message.get('references') is not None:
            found_references = re.findall(r'(\<.*?\>)', raw_message.get('references'), re.MULTILINE)
            self.references = list(set(found_references))
        else:
            self.references = []

    def __str__(self):
        return "message_id: %s, body: %s, patches: %s, subject: %s, msgdate: %s, from: %s, to: %s, cc: %s, date: %s, " \
               "in_reply_to: %s, references: %s" % (
            self.message_id, self.body, self.patches, self.subject, self.msgdate, getattr(self, 'from'), self.to,
            self.cc, self.date, self.in_reply_to, self.references
        )

    def __set_addresses(self, raw_message, charset):
        # message.getaddrlist returns a list of tuples
        # Each one of the tuples is like this
        # (name,email_address)
        #
        # For instance, if the header is
        #      To: Alice <alice@alice.com>, Bob <bob@bob.com>
        # it will return
        #      [('Alice','alice@alice.com'), ('Bob','bob@bob.com')]
        #
        # If the header is 'from', this list will contain only one element.
        # If the header is 'to' or 'cc', it may contain several items
        # (or it could also be an empty list when such header is missing
        #  in the original message).
        """
        Sets the addresses in the email

        :param raw_message: object of class :class:`email.message.Message`
        :param charset: charset that should be used
        """

        for header in ('from', 'to', 'cc'):
            if not raw_message.get(header):
                setattr(self, header, None)
                continue

            address = self.__check_spam_obscuring(self.__decode(raw_message.get(header), charset))
            addresses = self.__get_decoded_addresses(address, charset)
            setattr(self, header, addresses or None)

    @staticmethod
    def __set_msgdate(raw_message):
        """
        Sets the message date

        :param raw_message: object of class :class:`email.message.Message`
        """
        unix_from = raw_message.get_unixfrom()
        try:
            date_to_parse = unix_from.split(' ', 1)[1]
            parsed_date = parsedate_tz(date_to_parse)
            return datetime.datetime(*parsed_date)[:6]
        except AttributeError:
            return None

    def __create_message_id(self, raw_message):
        """
        Creates the mssage id, if none is given

        :param raw_message: object of class :class:`email.message.Message`
        """
        if raw_message.get('message-id') is not None:
            return raw_message.get('message-id')

        # Create unique identifier
        try:
            domain = getattr(self, 'from')[0][1].split('@')[1]
        except Exception:
            domain = 'mailingshark.localdomain'

        m = hashlib.md5(self.body.encode('utf-8')).hexdigest()
        return '<%s.mailingshark@%s>' % (m, domain)

    @staticmethod
    def __get_date(message):
        """
        Gets the date from the message

        :param message: object of class :class:`email.message.Message`
        """
        date = message.get('date')
        print(date)
        try:
            parsed_date = parsedate_tz(date)
        except AttributeError:
            date_parts = str(date).split(" ")[0:-1]
            date_parts.append("+0000")
            new_date = ' '.join(date_parts)
            logger.warning("Could not parse date %s. Try to format it differently: %s" % (date, new_date))
            parsed_date = parsedate_tz(new_date)

        if not parsed_date:
            msg_date = datetime.datetime(*(1979, 2, 4, 0, 0))
            tz_secs = 0
            return msg_date, tz_secs

        try:
            msg_date = datetime.datetime(*parsed_date[:6])
            # Workaround for `strftime` which allow dates higher than 1900.
            # And the MySQL module uses `strftime` to convert a datetime.
            if msg_date.year < 1900:
                # Usually we see years like 0102, but in case someboedy
                # set the date to 1800 or something alike, we leave only
                # the centuries before adding 1900.
                fixed_year = (msg_date.year % 1000) + 1900
                msg_date = msg_date.replace(year=msg_date.year + fixed_year)
        except ValueError:
            msg_date = datetime.datetime(*(1979, 2, 4, 0, 0))

        tz_secs = parsed_date[-1] or 0

        return msg_date, tz_secs

    def __get_decoded_addresses(self, address, charset):
        """
        Gets the decoded addresses

        :param address: email address
        :param charset: charset that should be used
        """
        result = []
        for name, email in getaddresses([address]):
            decoded_email = self.__decode(email, charset).replace('"', '')

            # If name is none, we just choose the first part of the email as name
            if not name or name is None:
                decoded_name = decoded_email.split('@')[0]
            else:
                decoded_name = self.__decode(name, charset)
            result.append((decoded_name,decoded_email))
        return result

    @staticmethod
    def __check_spam_obscuring(field):
        """
        Checks the field for spam obscuring (e.g., at instead of @)

        :param field: content of the email field
        """
        if not field:
            return field

        for pattern in EMAIL_OBFUSCATION_PATTERNS:
            if field.find(pattern) != -1:
                return field.replace(pattern, '@')

        return field

    @staticmethod
    def __get_body(raw_message, charset):
        """
        Gets the body for the message using a specific charset

        :param raw_message: object of class :class:`email.message.Message`
        :param charset: charset that should be used
        """
        # Non multipart messages should be straightforward
        if not raw_message.is_multipart():
            return to_unicode(raw_message.get_payload(decode=True), charset), None

        body = []
        patches = []
        # Include all the attached texts if it is multipart
        parts = [part for part in typed_subpart_iterator(raw_message, 'text')]
        for part in parts:
            part_charset = part.get_content_charset()
            part_body = part.get_payload(decode=True)
            part_subtype = part.get_content_subtype()
            if part_subtype == 'plain':
                body.append(to_unicode(part_body, part_charset))
            elif part_subtype in ('x-patch', 'x-diff'):
                patches.append(to_unicode(part_body, part_charset))

        return '\n'.join(body), patches

    @staticmethod
    def __decode(s, charset='latin-1', sep=u' '):
        """
        Decodes a header for a specific charset

        :param s: header
        :param charset: charset that should be used
        :param sep: seperator
        """

        charset = charset or 'latin-1'

        try:
            decoded_s = decode_header(s)
            r = sep.join([to_unicode(text, text_charset or charset) for text, text_charset in decoded_s])
        except Exception:
            logger.warning('WARNING: charset: %s' % charset)
            logger.warning('%s' % s)
            r = s

        return r
