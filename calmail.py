import caldav


def get_calendar():
    """
    Gets the calendar using credentials from `credentials.py`.
    """
    from credentials import USER, PASS, HOST, MAIL, CAL
    url = 'https://%s:%s@%s/dav/%s/%s' % (USER, PASS, HOST, MAIL, CAL)
    client = caldav.DAVClient(url)
    princ = caldav.Principal(client, url)
    return princ.calendars()[0]
