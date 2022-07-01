import json
import os


class Student:
    def __init__(self):

        self.username = None
        self.password = None
        self.schedule = []
        self.gcal_schedule = []
        self.load_login()

    def load_login(self):

        if os.path.exists('login_info.json'):
            with open('login_info.json', 'r') as f:
                creds = json.load(f)
                self.username = creds['username']
                self.password = creds['password']
        else:
            while True:
                try:
                    self.username = input("Username: ")
                    self.password = input("Password: ")
                except ValueError or TypeError:
                    pass
