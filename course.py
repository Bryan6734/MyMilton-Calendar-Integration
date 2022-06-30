class Course:
    def __init__(self, name, start_time, end_time, day, location=None):
        self.name = name
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.day = day

    def print_info(self):
        print(self.name, self.location, self.start_time, self.end_time, self.day, sep=" – ")




