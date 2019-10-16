import httplib2
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials
from tika import parser
import re


def book_calendar(start, end, attendees):
    refresh_token = "1/r_P28Uwy9XIAFZT0L9QxDXNxMwiumCUs0GG13BnLBUo"
    expires_in = 3599
    token = "ya29.Gl2oBu5AL8okK-wxYfyTb-mLEZBfXz1vIk-9512jbIxyr-of_2dBTsYdj0SCgPaEhP_zfOJ2hPXAkSt_" \
            "YngOvvp5bIlrZL5Hhg7l5R2_oIuyCLZlpucmcIki3qM8ANs"
    credentials = OAuth2Credentials(token, "487358077937-9glm8t6im13q3hdtthl3ktda6pit26c0.apps.googleusercontent.com",
                                    "lFaWrz7a5Xwhgd-3miVFdOUF", refresh_token, expires_in,
                                    'https://accounts.google.com/o/oauth2/token', "")
    http = httplib2.Http()
    credentials.authorize(http)
    service = build('calendar', 'v3', http=http)
    event = {
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',

        'start': {
            'dateTime': start,
            'timeZone': 'Asia/Calcutta',
        },

        'end': {
            'dateTime': end,
            'timeZone': 'Asia/Calcutta',
        },

        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],

        'attendees': attendees,

        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='sarang.m@consultadd.in', body=event).execute()
    return event.get('htmlLink')


def email_parser_from_file(file):
    raw = parser.from_file(file)
    match = re.search(r'[\w.-]+@[\w.-]+', raw['content'])
    emails = []
    if match:
        emails.append(match.group())
    return ','.join(emails)