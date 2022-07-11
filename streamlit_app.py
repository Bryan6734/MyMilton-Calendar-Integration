import streamlit as st

# import pandas as pd  # Pandas for data formatting
# from selenium import webdriver  # Google Chrome driver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service  # Loading URL
# from selenium.webdriver.common.by import By  # HTML Identifiers
# import course
# import gcal
import student

USER_FIELD_NAME = "UserLogin"  # HTML identifier
PASSWORD_FIELD_NAME = "UserPassword"  # HTML identifier
SUBMIT_FIELD_NAME = "df"  # HTML identifier
LOGIN_URL = "https://mymustangs.milton.edu/student/index.cfm?"
SCHEDULE_URL = "https://mymustangs.milton.edu/student/myschedule/fetch.cfm?TID=2&vSID=SUKB240&pdf=0"

st.title("My Milton Calendar Integration")
st.subheader("By Bryan Sukidi '24")
st.text("This app will allow you to integrate your MyMilton calendar with Google Calendar.")
st.text("First, you will have to log into your MyMilton account.")

username = st.text_input("Username:", "", type="default", placeholder="Type username here")
password = st.text_input("Password:", "", type="password", placeholder="Type password here")

student = student.Student()
student.username = username
student.password = password

# Configure Selenium settings
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,800")
chrome_options.add_argument("--headless")

# Instantiate the Selenium Chrome Driver
service = Service(executable_path="/Users/bryansukidi/Desktop/CS Projects/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the login page
driver.get(LOGIN_URL)

# Post username to username text box
username_field = driver.find_element(by=By.NAME, value=USER_FIELD_NAME)
username_field.send_keys(username)

# Post password to password text box
password_field = driver.find_element(by=By.NAME, value=PASSWORD_FIELD_NAME)
password_field.send_keys(password)

# Click submit button
submit_button = driver.find_element(by=By.NAME, value=SUBMIT_FIELD_NAME)
submit_button.click()

# Open the myMilton schedule page
driver.get(SCHEDULE_URL)
st.write("Accessing Website: ", driver.title)

# Get all table elements from HTML
html_elements = [elem.text.replace('\n', ' ') for elem in driver.find_elements(by=By.TAG_NAME, value="td")]

# Get time blocks "{Period Number} {XX:XX}" as row headers
timeblock_row_headers = [elem.text.replace('\n', " ") for elem in
                         driver.find_elements(by=By.CLASS_NAME, value="periodLabel")]
# Get weekdays "Monday"–"Friday" (x2 because Blue & Orange week) as column headers
weekday_col_headers = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Monday", "Tuesday", "Wednesday",
                       "Thursday", "Friday"]

# Use row headers (time blocks) to identify classes under time-block, and append to student schedule
for header in timeblock_row_headers:
    header_index = html_elements.index(header)
    week = [block if isinstance(block, str) and not (block.isspace() or not block) else "" for block in
            html_elements[header_index + 1: header_index + 11]]
    student.schedule.append(week)

# Create a Pandas Data Frame to clearly display data
row_headers = [x.split(" ")[-1] for x in timeblock_row_headers]

# Configure Pandas Data Frame printing settings
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Convert student schedule to Pandas Data Frame
student.schedule = pd.DataFrame(data=student.schedule, index=row_headers, columns=weekday_col_headers)
student.schedule = {'blue': student.schedule.iloc[:, :5], 'orange': student.schedule.iloc[:, 5:]}

st.write("----- Blue Week -----")
st.write(student.schedule['blue'].to_string(), "\n")

st.write("----- Orange Week -----")
st.write(student.schedule['orange'].to_string(), "\n")
