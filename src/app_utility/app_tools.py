import datetime


def get_most_recent_august_start():
    """
    Returns the most recent year in which the season starts in August.

    Returns
    -------
    numpy.ndarray
        The most recent year when the season starts in August.
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


def remove_starting_the(text):
    """
    Removes the substring 'the' from the beginning of the input string,
    regardless of case, and returns the modified string.

    Parameters
    ----------
    text : str
        The input string.

    Returns
    -------
    str
        The modified string with 'the' removed from the beginning.
    """
    if text.lower().startswith("the "):
        return text[4:].lstrip()
    return text


def generate_commentary(league_name, number_of_teams, year_start):
    league_name = remove_starting_the(league_name)

    commetnary_p1 = f"""The {league_name} is the highest level of the Fantasy English football league system. It is contested by {number_of_teams} clubs, and seasons typically run from August to May, with each team playing in 38 gameweeks. The league was founded in {year_start}."""
    return commetnary_p1
