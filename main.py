# Import packages
import json  # Reading username & password
import pandas as pd  # Pandas for data formatting
from selenium import webdriver  # Google Chrome driver
from selenium.webdriver.chrome.service import Service  # Loading URL
from selenium.webdriver.common.by import By  # HTML Identifiers
from selenium.webdriver.chrome.options import Options
import time  # System pausing
import course
import gcal


### ------ SELENIUM WEB SCRAPING ------ ###

# HTML Field Names
def main():
    USER_FIELD_NAME = "UserLogin"
    PASSWORD_FIELD_NAME = "UserPassword"
    SUBMIT_FIELD_NAME = "df"

    # Login Credentials (replace login details if necessary)
    with open('login_info.json', 'r') as f:
        creds = json.load(f)
        USER_USERNAME = creds['username']
        USER_PASSWORD = creds['password']

    # Student Calendar
    student_schedule_data = []  # Default Python list
    student_events = []
    student_df = []  # Pandas Data Frame

    # Instantiate the Selenium Chrome Driver
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,800")

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
    username_field.send_keys(USER_USERNAME)

    print(">>> Entering PASSWORD")
    # Post password to password text box
    password_field = driver.find_element(by=By.NAME, value=PASSWORD_FIELD_NAME)
    password_field.send_keys(USER_PASSWORD)

    print(">>> Submitting FORM")
    # Click submit button
    submit_button = driver.find_element(by=By.NAME, value=SUBMIT_FIELD_NAME)
    submit_button.click()

    ### ------ EXTRACTING SCHEDULE DATA ------ ###

    # GOAL: Use time-blocks (8:05-9:05) to find all classes under that time-block; then, combine all classes to
    # create a Data Frame with all classes

    # 8:05-9:05	    ENFV-1 HUS3-8 CS1H-3 SCHC-8 MA31a-2  CS1H-3           HUS3-8 SP3-4  SCHC-8
    # 9:05-9:25	                         SCHC-8             	          HUS3-8        SCHC-8 9:30-10:00    ASM-3 CLUB1-1
    # ADVS-1 HELP-1 CLUB3-1  CLMTG-3  CLUB4-1 ADVS-1 HELP-1 CLUB6-1

    # Open the myMilton schedule page
    driver.get("https://mymustangs.milton.edu/student/myschedule/fetch.cfm?TID=2&vSID=SUKB240&pdf=0")
    print("Accessing Website: ", driver.title)

    # Get all table elements
    all_schedule_elements = [elem.text.replace('\n', ' ') for elem in driver.find_elements(by=By.TAG_NAME, value="td")]

    # Get time blocks "{ordinal} {XX:XX}" as row headers
    row_headers = [elem.text.replace('\n', " ") for elem in
                   driver.find_elements(by=By.CLASS_NAME, value="periodLabel")]
    column_headers = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Monday", "Tuesday", "Wednesday",
                      "Thursday", "Friday"]

    # Use row headers (time blocks) to identify classes under time-block, and append to schedule_data
    for header in row_headers:
        header_index = all_schedule_elements.index(header)
        week = [block if isinstance(block, str) and not (block.isspace() or not block) else "" for block in
                all_schedule_elements[header_index + 1: header_index + 11]]
        student_schedule_data.append(week)

    # Create a Pandas Data Frame to clearly display data

    row_headers = [x.split(" ")[-1] for x in row_headers]

    student_df = pd.DataFrame(data=student_schedule_data, index=row_headers, columns=column_headers)

    # Configure Pandas Data Frame printing settings
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    # Partition Data Frame into two separate weeks (blue/orange)
    blue_student_df = student_df.iloc[:, :5]
    orange_student_df = student_df.iloc[:, 5:]

    print("----- Blue Week -----")
    print(blue_student_df.to_string(), "\n")

    print("----- Orange Week -----")
    print(orange_student_df.to_string(), "\n")

    time.sleep(5)
    # Convert Pandas Data Frame to iterable 2D numpy array
    blue_week = blue_student_df.to_numpy()

    # Create a new course object with all metadata for every course in week
    for row_idx, row in enumerate(blue_week):
        for col_idx, col in enumerate(row):
            print("--------")

            # Check if column is a parsable string (not just whitespace)
            if isinstance(col, str) and not (col.isspace() or not col):
                try:
                    # Split & unpack column into course_name and course_location
                    # "ENFV WRN203" -> "ENFV", "WRN203"
                    course_name, course_location = col.split(" ")

                # If location is omitted, set course_name to column 
                except ValueError:
                    course_name = col
                    course_location = ""

                # Unpack start and end times from the row header that the current column is located in
                start_time, end_time = row_headers[row_idx].split('-')

                course_metadata = course.Course(name=course_name, start_time=start_time, end_time=end_time,
                                                day=col_idx, period=row_idx, location=course_location)
                student_events.append(course_metadata)
                course_metadata.print_info()

            else:
                if 5 <= row_idx <= 6:
                    print("Lunch")
                else:
                    print("Free")

    ### ------ UPLOADING GOOGLE CALENDAR EVENTS ------ ###

    creds = gcal.load_credentials()

    while True:
        try:
            response = input("[CREATE] or [DELETE] events? \n").lower()

            if response == 'create':
                for student_event in student_events:
                    student_event.print_info()
                    # Create google calendar event
                    # Add ID to event_IDS
                    gcal.create_event(creds=creds, event=student_event.generate_event())
                # Upload to JSON
                gcal.log_event_ids()
            elif response == 'delete':
                gcal.delete_all_events(creds=creds)

            break
        except TypeError or ValueError:
            pass

    time.sleep(5)
    driver.quit()

    # idea: store a json file of all of user's calendar ids


if __name__ == '__main__':
    main()
