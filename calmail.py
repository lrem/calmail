import caldav
import datetime
import icalendar

DAYS_BEFORE = [5, 1, 0]


def get_calendar():
    """
    Get the calendar using credentials from `credentials.py`.
    """
    from credentials import USER, PASS, HOST, MAIL, CAL
    url = 'https://%s:%s@%s/dav/%s/%s' % (USER, PASS, HOST, MAIL, CAL)
    client = caldav.DAVClient(url)
    princ = caldav.Principal(client, url)
    return princ.calendars()[0]


def filter_events(cal):
    """
    Get the events in *cal* that have a date that is one of `DAYS_BEFORE`
    in the future.
    """
    results = []
    for delta in DAYS_BEFORE:
        day = datetime.date.today() + datetime.timedelta(days=delta)
        results.extend(cal.date_search(day, day + datetime.timedelta(days=1)))
        print day
    return results


def parse_event(event):
    """
    Return a hash with interesting fields of the `event`.
    The fields are:
        - `SUMMARY` for the event name
        - `DESCRIPTION` for long description
    """
    ice = icalendar.Calendar.from_ical(event.data)
    ret = {key: '' for key in ('SUMMARY', 'DESCRIPTION')}
    found = False
    for component in ice.walk():
        if component.name == 'VEVENT':
            assert not found, "Multiple 'VEVENT' fields in event"
            found = True
            for key in ret:
                if key in component:
                    ret[key] = component[key]
    assert found, "No 'VEVENT' in event"
    return ret
