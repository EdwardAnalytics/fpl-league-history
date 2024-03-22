import datetime

def get_most_recent_august_start():
    """
    This is used to get the most recent start of season year
    """

    # Get the current date
    current_date = datetime.datetime.now()

    # Set the month and day to August 1st of the current year
    august_start = datetime.datetime(current_date.year, 8, 1)

    # If the current date is before August 1st, we need to go back to the previous year
    if current_date.month < 8:
        august_start = august_start.replace(year=current_date.year - 1)

    august_start = august_start.year

    return august_start
