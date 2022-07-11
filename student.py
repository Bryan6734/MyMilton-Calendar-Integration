import json
import os
from json import JSONDecodeError

class Student:
    def __init__(self):

        self.username = None
        self.password = None
        self.schedule = []
        self.gcal_schedule = []

    def load_streamlit_login(self, username, password):
        self.username = username
        self.password = password
        with open('login_info.json', 'w') as login_info:
            json.dump({'username': self.username, 'password': self.password}, login_info)

    def load_login(self):
        try:
            if os.path.exists('login_info.json'):
                with open('login_info.json', 'r') as login_info:
                    login_info = json.load(login_info)
                    self.username = login_info['username']
                    self.password = login_info['password']
            else:
                self.username = input("Username: ")
                self.password = input("Password: ")
                with open('login_info.json', 'w') as login_info:
                    json.dump({'username': self.username, 'password': self.password}, login_info)
        except JSONDecodeError:
            print("Invalid login info")
            os.remove('login_info.json')
            self.load_login()
