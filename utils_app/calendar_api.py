import httplib2
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials

SCRUM_MASTER = {
    'Nzyme': 'sarang.m@consultadd.in',
    'Okyte': 'sarang.m@consultadd.in',
    'Boto3': 'sarang.m@consultadd.in',
    'Ioneq': 'sarang.m@consultadd.in',
    'Zioqu': 'sarang.m@consultadd.in',
    'Octane': 'sarang.m@consultadd.in',
    'Induci': 'sarang.m@consultadd.in',
    'GoKronos': 'sarang.m@consultadd.in',
    'Pythonwise': 'sarang.m@consultadd.in',
    'Consultadd': 'sarang.m@consultadd.in',
    'Netresolute': 'sarang.m@consultadd.in',
}


def calendar_con():
    refresh_token = "1/pC5KN2aCTRx_R4tS8xEGlUCZx6LI4pjwkDo71bhgwrw"
    expires_in = 3599
    token = "ya29.Glv2BgSkQqLfsWiPn3_S1dZTx_TJPIQBcGsCWcBTmZife20z7ik6b7IzNkUv2iWlc9UaYbEgj4e8I" \
            "Tkk5WAKYFUz1wVKk1xokIWHbe9GJ-XU7uPo57NTFIUELRLN"
    credential = OAuth2Credentials(token, "414060049848-lhccvdlscbmoap54i1qk5333oobsfbf3.apps.googleusercontent.com",
                                   "Kj-4GHm_eRdIKq_Vrlh7Ek78", refresh_token, expires_in,
                                   'https://accounts.google.com/o/oauth2/token', "")

    http = httplib2.Http()
    credential.authorize(http)
    service = build('calendar', 'v3', http=http)
    return service


def book_calendar(data):
    service = calendar_con()
    consultant = data["consultant"]
    consultant_profile = data["consultant_profile"]
    user = data["user"]
    submission = data["submission"]
    lead = data["lead"]

    description = '''
    <strong>Marketer Name - {}</strong>
    <strong>Employer - {}</strong>

    <strong>consultant Details: </strong>

        Name - {}
        DOB - {}
        SSN - {}
        VISA: {}

        Skype id - {}

        Education - {}

        Email - {}

    <strong>Interview Details - </strong>

        {}

    <strong>Position Details:</strong>

        Location = {}
        Job Title - {}
        
    <strong>Job Description:</strong>

        {}

    '''.format(user.full_name, user.team.name, consultant.name, consultant_profile.dob, consultant.ssn,
               consultant_profile.visa_type, consultant_profile.links, consultant_profile.education,
               consultant_profile.email, data["description"], consultant_profile.location, lead.job_title,
               lead.job_desc)
    event = {
        'summary': data["summary"],

        'description': description,

        'start': {
            'dateTime': data["start"],
            'timeZone': 'America/New_York',
        },

        'end': {
            'dateTime': data["end"],
            'timeZone': 'America/New_York',
        },

        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=1'
        ],

        'attendees': data["attendees"],

        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    event = service.events().insert(calendarId='admin@log1.com', body=event).execute()
    return event


def update_calendar(event_id, data):
    service = calendar_con()
    event = {
        'summary': data["summary"],
        'description': data["description"],

        'start': {
            'dateTime': data["start"],
            'timeZone': 'America/New_York',
        },

        'end': {
            'dateTime': data["end"],
            'timeZone': 'America/New_York',
        },

        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=1'
        ],

        'attendees': data["attendees"],

        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    updated_event = service.events().update(calendarId='admin@log1.com', eventId=event_id, body=event).execute()
    return updated_event['id']


def get_inteviews(data):
    service = calendar_con()
    page_token = None
    count = 0
    calendar_data = []
    time_min = data["start"] + '06:00:00-04:00'
    time_max = data["end"] + '23:59:00-04:00'
    while True:
        events = service.events().list(calendarId=data["email"],
                                       pageToken=page_token,
                                       singleEvents=True,
                                       orderBy="startTime",
                                       timeMin=time_min,
                                       timeMax=time_max
                                       ).execute()
        visibility = True
        for event in events["items"]:
            if "visibility" in event:
                visibility = False
                data = {
                    "id": event["id"],
                    "updated": event["updated"],
                    "start": event["start"]["dateTime"],
                    "end": event["end"]["dateTime"],
                }
            else:
                data = {
                    "id": event["id"],
                    "title": event["summary"] if "summary" in event else "",
                    "description": event["description"] if "description" in event else "",
                    "created": event["created"],
                    "updated": event["updated"],
                    "start": event["start"]["dateTime"],
                    "end": event["end"]["dateTime"],
                    "attendees": [i["email"] for i in event["attendees"]] if "attendees" in event else [],
                    "attachments": [{"fileUrl": i["fileUrl"], "title": i["title"]} for i in
                                    event["attachments"]] if "attachments" in event else []
                }
            count += 1
            calendar_data.append(data)
        page_token = events.get('nextPageToken')
        if not page_token:
            return calendar_data, visibility


def delete_calendar_booking(event_id):
    service = calendar_con()
    service.events().delete(calendarId='admin@log1.com', eventId=event_id).execute()
