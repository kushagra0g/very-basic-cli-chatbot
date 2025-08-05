import datetime

# Function to get current time
def get_timestamp():
    now = datetime.datetime.now()
    now = now.strftime("%d/%m/%Y %I:%M:%S %p")
    return now

