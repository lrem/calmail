#!/usr/bin/env python
"""
iCal to email notifications
===========================

By Remigiusz `lRem` Modrzejewski.

This script is created to automatically send announcements
of the *weekly* seminars of COATI team.
You're free to adapt it to your needs,
but it would be nice if you kept a link to my website in mail ;)

License Info
------------

Copyright (c) 2013, Remigiusz 'lRem' Modrzejewski
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
      * Neither the name of INRIA, I3S, CNRS, UNS, PACA nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL Remigiusz Modrzejewski BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
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
    msg['To'] = ', '.join(TO)

    smtp = smtplib.SMTP(SMTP)
    smtp.sendmail(MAIL, TO, msg.as_string())


def parse_error(day, exc):
    """
    Send an information about parse error to `EMAIL` from `credentials.py`.
    """
    from credentials import SMTP, MAIL
    msg = MIMEText('Parsing failed for an event on day ' + str(day) +
                   "\n\nException: " + str(type(exc)) + ' ' + str(exc))
    msg['Subject'] = 'CALMAIL PARSE ERROR'
    msg['FROM'] = MAIL
    msg['TO'] = MAIL
    smtp = smtplib.SMTP(SMTP)
    smtp.sendmail(MAIL, [MAIL], msg.as_string())


def sending_error(parsed, day, ddesc, exc):
    """
    Send an information about sending error to `EMAIL` from `credentials.py`.
    """
    from credentials import SMTP, MAIL
    msg = MIMEText('Sending failed for an event on day ' + str(day) +
                   "\n\nException: " + str(type(exc)) + ' ' + str(exc) +
                   "\n\nParsed: \n" + str(parsed))
    msg['Subject'] = 'CALMAIL SENDING ERROR'
    msg['FROM'] = MAIL
    msg['TO'] = MAIL
    smtp = smtplib.SMTP(SMTP)
    smtp.sendmail(MAIL, [MAIL], msg.as_string())


def main():
    print "Getting calendar"
    cal = get_calendar()
    print "Done"
    for delta, ddesc in zip(DELTAS, DELTA_DESCRIPTIONS):
        day = datetime.date.today() + datetime.timedelta(days=delta)
        print "Searching events for", day, '(', ddesc, ')'
        evs = filter_events(cal, day)
        print len(evs), "found"
        for event in evs:
            try:
                parsed = parse_event(event)
            except Exception, exc:
                parse_error(day, exc)
            else:
                print "Sending email about", parsed['SUMMARY']
                try:
                    send_mail(parsed, day, ddesc)
                except Exception, exc:
                    sending_error(parsed, day, ddesc, exc)
                print "Done"

if __name__ == '__main__':
    main()
