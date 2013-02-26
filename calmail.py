import caldav
import datetime
import icalendar
import smtplib
import re

from email.mime.text import MIMEText

DELTAS = [5, 1, 0]
DELTA_DESCRIPTIONS = ['in 5 days', 'tomorrow', 'today']


def get_calendar():
    """
    Get the calendar using credentials from `credentials.py`.
    """
    from credentials import USER, PASS, HOST, MAIL, CAL
    url = 'https://%s:%s@%s/dav/%s/%s' % (USER, PASS, HOST, MAIL, CAL)
    client = caldav.DAVClient(url)
    princ = caldav.Principal(client, url)
    return princ.calendars()[0]


def filter_events(cal, day):
    """
    Get the events in *cal* that happen the given `day`.
    """
    return cal.date_search(day, day + datetime.timedelta(days=1))

        #day = datetime.date.today() + datetime.timedelta(days=delta)


def parse_event(event):
    """
    Return a hash with interesting fields of the `event`.
    """
    ice = icalendar.Calendar.from_ical(event.data)
    ret = {key: '' for key in ('SUMMARY', 'LOCATION', 'TIME')}
    found = False
    for component in ice.walk():
        if component.name == 'VEVENT':
            assert not found, "Multiple 'VEVENT' fields in event"
            found = True
            for key in ret:
                if key in component:
                    ret[key] = component[key]
            ret['TIME'] = str(component['DTSTART'].dt.time())
            ret.update(parse_description(component['DESCRIPTION']))
    assert found, "No 'VEVENT' in event"
    return ret


def parse_description(dsc):
    """
    Parse the given string into a hash.
    The string format is `key: value`,
    where key gets converted to upper case
    and value extends until a new line.
    A special last field `Abstract:` extends until the end of string.
    """
    meta, abstract = re.split('abstract:\s*\n*', dsc, flags=re.I)
    ret = {'ABSTRACT': abstract}
    for line in meta.splitlines():
        if ':' in line:
            key, value = re.split('\s*:\s*', line, 1)
            key = key.upper()
            ret[key] = value
    return ret


def send_mail(parsed_event, date, delta_description):
    """
    Send a mail alert about the `parsed_event`,
    using SMTP and credentials from `credentials.py`;
    mail template is taken from `mail_template.py`.
    """
    from mail_template import SUBJECT, TEMPLATE, TO
    from credentials import SMTP, MAIL
    parsed_event['DATE'] = date
    parsed_event['DELTA'] = delta_description

    msg = MIMEText(TEMPLATE % parsed_event)
    msg['Subject'] = SUBJECT + ' ' + str(date)
    msg['From'] = MAIL
    msg['To'] = TO

    smtp = smtplib.SMTP(SMTP)
    smtp.sendmail(MAIL, [TO], msg.as_string())
