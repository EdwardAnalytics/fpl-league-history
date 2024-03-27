import datetime
import pandas as pd


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
    """
    Generate commentary for a football league.

    This function generates a descriptive commentary about a football league,
    incorporating details such as the league's name, the number of teams
    participating, and the year it was founded.

    Parameters
    ----------
    league_name : str
        The name of the football league.
    number_of_teams : int
        The number of teams in the league.
    year_start : int
        The year the league was founded.

    Returns
    -------
    commentary : str
        A descriptive commentary about the football league,
        including details such as the league name, number of teams,
        and the founding year.
    """
    league_name = remove_starting_the(league_name)

    commetnary_p1 = f"""The {league_name} is the highest level of the Fantasy English football league system. It is contested by {number_of_teams} clubs, and seasons typically run from August to May, with each team playing in 38 gameweeks. The league was founded in {year_start}."""
    return commetnary_p1


def get_team_plot(df, team, value_to_plot):
    """
    Extract data for a specific team and a chosen value to plot.

    This function filters a DataFrame to extract data for a specific team and a chosen value to plot,
    such as goals scored, points earned, or any other relevant metric.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data to be filtered.
    team : str
        The name of the team for which data will be extracted.
    value_to_plot : str
        The name of the column containing the values to be plotted.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the filtered data for the specified team,
        with the 'Season' and the chosen value to plot as columns.
    """
    filtered_df = df[df["Team"] == team][["Season", value_to_plot]].rename(
        columns={value_to_plot: team}
    )
    return filtered_df


def get_league_plot(df, teams, value_to_plot):
    """
    Extract data for multiple teams and a chosen value to plot.

    This function filters a DataFrame to extract data for multiple teams and a chosen value to plot,
    such as goals scored, points earned, or any other relevant metric, and combines them into a single DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data to be filtered.
    teams : list of str
        A list containing the names of the teams for which data will be extracted.
    value_to_plot : str
        The name of the column containing the values to be plotted.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the filtered data for all the specified teams,
        with the 'Season' as the index and each team's data for the chosen value to plot as columns.
    """
    for i in range(0, len(teams)):
        if i == 0:
            df_plot = get_team_plot(df, team=teams[0], value_to_plot=value_to_plot)
        else:
            df_stage = get_team_plot(df, team=teams[i], value_to_plot=value_to_plot)
            df_plot = pd.merge(df_plot, df_stage, on="Season", how="outer")
    return df_plot
