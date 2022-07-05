from __future__ import print_function
import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
BLUE_CALENDER_ID = 'ref72r792mf33o1ts1g75abucc@group.calendar.google.com'
ORANGE_CALENDER_ID = 'ssgcd203phkqi7goarojd7dm04@group.calendar.google.com'
all_event_ids = []


def load_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def main():
    # Load Google OAuth credentials
    print("ran")


## CalenderList API Functions

def select_calendar_list(creds):
    service = build('calendar', 'v3', credentials=creds)
    page_token = None

    # List all calendars
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        # Iterate through each of the user's calendars and print the calendar ID and name
        for idx, calendar_list_entry in enumerate(calendar_list['items']):
            print(idx, calendar_list_entry['summary'], calendar_list_entry['id'], sep=" ")
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # Get user input
    while True:
        try:
            ids = []
            blue_choice = int(input("Select a calendar for BLUE week: "))
            orange_choice = int(input("Select a calendar for ORANGE week: "))

            for choice in [blue_choice, orange_choice]:
                if 0 <= choice < len(calendar_list['items']):
                    ids.append(calendar_list['items'][choice]['id'])
                else:
                    print("Invalid input")

            if ids and len(ids) == len(set(ids)):
                print(f"Calendars Selected:",
                      f"Blue: {calendar_list['items'][blue_choice]['summary']}",
                      f"Orange: {calendar_list['items'][orange_choice]['summary']}", sep="\n")
                choice = input("Is this correct? (y/n) ").lower().strip()
                if choice == "y":
                    break
        except ValueError:
            print("Invalid input")
    print(ids)
    return ids


def create_calendar_list(creds):
    service = build('calendar', 'v3', credentials=creds)


def create_calendar_list(creds, week, hex_code):
    calendar_list = {
        'id': 'TEST CALENDAR',
        'backgroundColor': hex_code
    }

    service = build('calendar', 'v3', credentials=creds)
    created_calendar_list_entry = service.calendarList().insert(body=calendar_list).execute()
    print(created_calendar_list_entry['summary'])


## CalendarEvent API Functions

def log_event_ids():
    # Log all_event_ids to JSON file
    with open('event_ids.json', 'w') as f:
        json.dump(all_event_ids, f)
    # print("log", all_event_ids)


def delete_all_events(creds):
    try:
        service = build('calendar', 'v3', credentials=creds)

        with open('event_ids.json', 'r') as f:
            # Load all ids from JSON file
            trash_ids = json.loads(f.read())
            print(trash_ids)
            # Delete each event from Calendar and event_id from list
            for event_id in trash_ids:
                # Delete calendar event
                service.events().delete(calendarId=BLUE_CALENDER_ID, eventId=event_id).execute()
        all_event_ids.clear()
        os.remove('event_ids.json')

    except HttpError as error:
        print('An error occurred: %s' % error)
    except FileNotFoundError:
        print('No events to delete')


def create_event(creds, event):
    try:
        service = build('calendar', 'v3', credentials=creds)
        recurring_event = service.events().insert(calendarId=BLUE_CALENDER_ID, body=event).execute()

        # Add event_id to all_event_ids when event is created
        all_event_ids.append(recurring_event['id'])

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
