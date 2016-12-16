import datetime

MAILMAN_DATE_FORMAT = '%Y-%B'
MAILMAN_ALT_DATE_FORMAT = '%Y-%m'
MOD_MBOX_DATE_FORMAT = '%Y%m'


def current_month(mailing_list_updated):
    """Get a tuple containing the current month in different formats"""
    # Assuming this is run daily, it's better to take yesterday's date,
    # to ensure we get all of last month's email when the month rolls over.
    if mailing_list_updated is None:
        return []

    last_mailing_list_update = mailing_list_updated + datetime.timedelta(days=-1)
    last_mailing_list_update_month_mailman = last_mailing_list_update.strftime(MAILMAN_DATE_FORMAT)
    last_mailing_list_update_month_mailman_alt = last_mailing_list_update.strftime(MAILMAN_ALT_DATE_FORMAT)
    last_mailing_list_update_month_mod_mox = last_mailing_list_update.strftime(MOD_MBOX_DATE_FORMAT)
    return last_mailing_list_update_month_mailman, last_mailing_list_update_month_mailman_alt, \
           last_mailing_list_update_month_mod_mox


def find_month_were_mailing_list_was_last_parsed(link, mailing_list_updated):
    """Find the current month in the given string.
    If the month is found, the function will return a string
    containing the current month. Otherwise returns None."""

    for this_month in current_month(mailing_list_updated):
        idx = link.find(this_month)
        if idx > -1:
            return this_month
    return None
