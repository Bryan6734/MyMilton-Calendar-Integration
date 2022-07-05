# Import packages
import time  # System pausing

import pandas as pd  # Pandas for data formatting
from selenium import webdriver  # Google Chrome driver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # Loading URL
from selenium.webdriver.common.by import By  # HTML Identifiers

import course  # Project imports
import gcal
import student

## Global Variable Declarations
USER_FIELD_NAME = "UserLogin"  # HTML identifier
PASSWORD_FIELD_NAME = "UserPassword"  # HTML identifier
SUBMIT_FIELD_NAME = "df"  # HTML identifier
SCHEDULE_URL = "https://mymustangs.milton.edu/student/myschedule/fetch.cfm?TID=2&vSID=SUKB240&pdf=0"

# Instantiate a new Student object
student = student.Student()


### ------ SELENIUM WEB SCRAPING ------ ###

# HTML Field Names
def main():
    # Load student login info
    student.load_login()

    # Configure Selenium settings
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,800")

    # Instantiate the Selenium Chrome Driver
    service = Service(executable_path="/Users/bryansukidi/Desktop/CS Projects/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the myMilton login website
    driver.get("https://mymustangs.milton.edu/student/index.cfm?")
    print("Accessing Website: ", driver.title)

    # Wait 0.5 seconds for website loading time (Selenium is asynchronous)
    driver.implicitly_wait(0.5)

    # Post username to username text box
    print(">>> Entering USERNAME")
    username_field = driver.find_element(by=By.NAME, value=USER_FIELD_NAME)
    username_field.send_keys(student.username)

    print(">>> Entering PASSWORD")
    # Post password to password text box
    password_field = driver.find_element(by=By.NAME, value=PASSWORD_FIELD_NAME)
    password_field.send_keys(student.password)

    print(">>> Submitting FORM")
    # Click submit button
    submit_button = driver.find_element(by=By.NAME, value=SUBMIT_FIELD_NAME)
    submit_button.click()

    # Validate Login
    print(">>> Validating Login")
    print("Accessing Website: ", driver.title)
    ### ------ EXTRACTING SCHEDULE DATA ------ ###

    # Open the myMilton schedule page
    driver.get(SCHEDULE_URL)
    print("Accessing Website: ", driver.title)

    # Get all table elements from HTML
    html_elements = [elem.text.replace('\n', ' ') for elem in driver.find_elements(by=By.TAG_NAME, value="td")]

    # Get time blocks "{Period Number} {XX:XX}" as row headers
    timeblock_row_header = [elem.text.replace('\n', " ") for elem in
                            driver.find_elements(by=By.CLASS_NAME, value="periodLabel")]
    # Get weekdays "Monday"–"Friday" (x2 because Blue & Orange week) as column headers
    weekday_col_headers = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Monday", "Tuesday", "Wednesday",
                           "Thursday", "Friday"]

    # Use row headers (time blocks) to identify classes under time-block, and append to student schedule
    for header in timeblock_row_header:
        header_index = html_elements.index(header)
        week = [block if isinstance(block, str) and not (block.isspace() or not block) else "" for block in
                html_elements[header_index + 1: header_index + 11]]
        student.schedule.append(week)

    # Create a Pandas Data Frame to clearly display data
    timeblock_row_header = [x.split(" ")[-1] for x in timeblock_row_header]

    # Configure Pandas Data Frame printing settings
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    # Convert student schedule to Pandas Data Frame
    student.schedule = pd.DataFrame(data=student.schedule, index=timeblock_row_header, columns=weekday_col_headers)
    student.schedule = {'blue': student.schedule.iloc[:, :5], 'orange': student.schedule.iloc[:, 5:]}

    print("----- Blue Week -----")
    print(student.schedule['blue'].to_string(), "\n")

    print("----- Orange Week -----")
    print(student.schedule['orange'].to_string(), "\n")

    for week in student.schedule:
        week_color = week
        week = student.schedule[week].to_numpy()
        for row_idx, row in enumerate(week):
            for col_idx, col in enumerate(row):
                if isinstance(col, str) and not (col.isspace() or not col):
                    try:
                        # Split & unpack column into course_name and course_location
                        # "ENFV WRN203" -> "ENFV", "WRN203"
                        course_name, course_location = col.split(" ")

                    except ValueError:
                        # If location is omitted, set course_name to column
                        course_name = col
                        course_location = ""

                    # Unpack start and end times from the row header that the current column is located in
                    start_time, end_time = timeblock_row_header[row_idx].split('-')

                    # Create course object
                    course_metadata = course.Course(name=course_name, start_time=start_time, end_time=end_time,
                                                    day=col_idx, period=row_idx, week=week_color,
                                                    location=course_location)
                    student.gcal_schedule.append(course_metadata)
                    course_metadata.print_info()

                else:
                    if 5 <= row_idx <= 6:
                        print("Lunch")
                    else:
                        print("Free")

    ### ------ UPLOADING GOOGLE CALENDAR EVENTS ------ ###

    creds = gcal.load_credentials()
    # gcal.select_calendar_list(creds=creds)
    # gcal.create_calendar_list(creds=creds, week='blue', hex_code='#003366')

    while True:
        try:
            response = input("[CREATE] or [DELETE] events? \n").lower()

            if response == 'create':
                for student_event in student.gcal_schedule:
                    student_event.print_info()
                    # Create google calendar event
                    # Add ID to event_IDS
                    gcal.create_event(creds=creds, event=student_event.generate_event())
                    student_event.event_id = gcal.all_event_ids[-1]
                    print("Event ID: ", student_event.event_id)
                # Upload to JSON
                gcal.log_event_ids()
                print("event ids: ", gcal.all_event_ids)
            elif response == 'delete':
                gcal.delete_all_events(creds=creds)
                break

        except TypeError or ValueError:
            pass
        except EOFError:
            break

    driver.quit()


if __name__ == '__main__':
    main()
