import datetime


# First day of classes: September 12th, 2022 Blue Week
# date = datetime.datetime(2020, 2, 20)
# date += datetime.timedelta(days=1)


class Course:
    def __init__(self, name, start_time, end_time, day, period, location=None):
        self.name = name
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.day = day
        self.period = period

        # Convert into ISO datetime format to be passed into Google Calendar API
        self.start_datetime_ISO, self.end_datetime_ISO = self.get_datetime()

    def print_info(self):
        print(self.name, self.location, self.start_time, self.end_time, self.day, sep=" – ")

    def get_datetime(self):
        year = 2022
        month = 9
        day = 12 + self.day

        # Unpack hours and minutes
        # Convert hours to military time
        start_hour, start_minutes = [int(t) for t in self.start_time.split(":")]
        end_hour, end_minutes = [int(t) for t in self.end_time.split(":")]

        if self.period == 6:
            end_hour += 12
        elif self.period > 6:
            start_hour += 12
            end_hour += 12

        print(start_hour)

        start_datetime = datetime.datetime(year, month, day, start_hour, start_minutes).isoformat()
        end_datetime = datetime.datetime(year, month, day, end_hour, end_minutes).isoformat()

        return start_datetime, end_datetime

    def generate_event(self):
        return {
            'summary': self.name,
            'location': self.location,
            'start': {
                'dateTime': self.start_datetime_ISO,
                'timeZone': 'America/New_York'
            },
            'end': {
                'dateTime': self.end_datetime_ISO,
                'timeZone': 'America/New_York'
            },
            'recurrence': [
                'RRULE:FREQ=WEEKLY;UNTIL=20220801T170000Z',
            ]
        }
