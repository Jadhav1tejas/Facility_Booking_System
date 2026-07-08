from datetime import datetime

def calculate_duration(start_time, end_time):

    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")

    duration = (end - start).seconds / 3600

    return duration