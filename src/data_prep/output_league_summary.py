import inflect
import pandas as pd


def get_current_champions(df, season_overview):
    """
    Retrieve information about the current champions.

    This function identifies the current champions based on the provided DataFrame containing season data and the season overview DataFrame. It returns a string describing the current champions, including the manager's name, team name, number of titles won, and the season when they became champions.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing season data.
    season_overview : pandas.DataFrame
        DataFrame summarizing the performance of teams across seasons.

    Returns
    -------
    current_champions : str
        A string describing the current champions.

    """
    current_champions_index = df["season_name"].idxmax()

    current_champions_team_name = df.loc[current_champions_index, "team_name"]
    current_champions_manager_name = df.loc[current_champions_index, "manager_name"]
    current_champions_season_name = df.loc[current_champions_index, "season_name"]

    # Get title number and append "st", "nd", "rd" for "1st", "2nd", "3rd" etc.
    title_number = season_overview.loc[
        season_overview["team_name"] == current_champions_team_name, "seasons_won"
    ]
    p = inflect.engine()
    title_number = p.ordinal(int(title_number))

    current_champions = f"{current_champions_manager_name}: {current_champions_team_name} ({title_number} title) ({current_champions_season_name})"

    return current_champions


def get_most_wins(df):
    """
    Retrieve information about the teams with the most championships.

    This function identifies the teams with the most championships based on the provided DataFrame containing season data. It returns a string describing the teams with the most championships, including the manager's name, team name, and the number of titles won.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing season data.

    Returns
    -------
    most_season_won_teams_str : str
        A string describing the teams with the most championships.

    """
    most_seasons_won = df["seasons_won"].max()

    most_season_won_teams = df.loc[
        df["seasons_won"] == most_seasons_won,
        ["manager_name", "team_name", "seasons_won"],
    ].to_dict(orient="records")

    most_season_won_teams_list = []
    for team in most_season_won_teams:
        manager_name = team["manager_name"]
        team_name = team["team_name"]
        seasons_won = team["seasons_won"]
        teams_str = f"{manager_name}: {team_name} ({seasons_won} titles)"
        most_season_won_teams_list.append(teams_str)
    most_season_won_teams_str = "; ".join(most_season_won_teams_list)
    return most_season_won_teams_str


def get_best_rank_points(df, column):
    """
    Retrieve information about teams achieving the best rank or points.

    This function identifies the teams that achieved the best rank or the most points in a season based on the provided DataFrame containing season data. It returns a string describing the teams, including the manager's name, team name, the best rank or points achieved, and the season.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing season data.
    column : str
        Column name indicating the criteria (rank or total points).

    Returns
    -------
    best_teams_str : str
        A string describing the teams achieving the best rank or points.

    """
    if column == "rank":
        best = df[column].min()
        column_alias = "Rank"
    elif column == "total_points":
        best = df[column].max()
        column_alias = "Points"

    best_teams = df.loc[
        df[column] == best,
        ["manager_name", "team_name", "rank", "total_points", "season_name"],
    ].to_dict(orient="records")

    best_teams_list = []
    for team in best_teams:
        manager_name = team["manager_name"]
        team_name = team["team_name"]
        best_value = "{:,}".format(team[column])
        season_name = team["season_name"]
        teams_str = (
            f"{manager_name}: {team_name}: {column_alias}: {best_value} ({season_name})"
        )
        best_teams_list.append(teams_str)
    best_teams_str = "; ".join(best_teams_list)

    return best_teams_str


# Get number of teams in league
def get_number_of_teams_league(team_data):
    """
    Retrieve the number of teams in the league.

    This function calculates the number of teams participating in the league based on the provided league data.

    Parameters
    ----------
    team_data : list
        List containing data about the league.

    Returns
    -------
    number_of_teams_league : int
        The number of teams in the league.
    """
    number_of_teams_league = len(team_data)
    return number_of_teams_league


# Get first season data appears
def get_first_Season_year_data(df):
    """
    Retrieve the first season year data appears.

    This function identifies the year of the first season in the provided DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing season data.

    Returns
    -------
    first_Season_year_data : str
        The year of the first season in the DataFrame.
    """
    first_Season_year_data = df["season_name"].min()
    first_Season_year_data = first_Season_year_data[0:4]
    return first_Season_year_data


def get_league_name(league_data):
    """
    Retrieve the league name.

    This function extracts the name of the league from the provided league data.

    Parameters
    ----------
    league_data : dict
        Dictionary containing data about the league.

    Returns
    -------
    league_name : str
        The name of the league.
    """
    league_name = league_data["league"]["name"]
    return league_name


def get_league_summary_kpis(
    first_Season_year_data,
    number_of_teams_league,
    current_champions_output,
    most_season_won_teams_str_output,
    best_points_teams_str_output,
    best_rank_teams_str,
):
    """
    Generate a summary of key performance indicators (KPIs) for the league.

    This function compiles key performance indicators such as founding year, number of teams, current champions, most championships won, most points in a season, and highest rank in a season into a DataFrame.

    Parameters
    ----------
    first_Season_year_data : str
        The year of the first season.
    number_of_teams_league : int
        The number of teams in the league.
    current_champions_output : str
        Information about the current champions.
    most_season_won_teams_str_output : str
        Information about the teams with the most championships.
    best_points_teams_str_output : str
        Information about teams achieving the most points in a season.
    best_rank_teams_str : str
        Information about teams achieving the highest rank in a season.

    Returns
    -------
    pandas.DataFrame
        A DataFrame summarizing key performance indicators for the league.
    """
    d = {
        "Founded": first_Season_year_data,
        "Number of teams": str(number_of_teams_league),
        "Current Champions": current_champions_output,
        "Most Championships": most_season_won_teams_str_output,
        "Most Points in a Season": best_points_teams_str_output,
        "Highest Rank in a Season": best_rank_teams_str,
    }
    league_summary_kpis = pd.DataFrame(data=d, index=[0]).T
    return league_summary_kpis
