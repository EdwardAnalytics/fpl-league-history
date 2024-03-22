import inflect
import pandas as pd


def get_current_champions(df, season_overview):
    """ """
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
    """ """
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
    """ """
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
def get_number_of_teams_league(league_data):
    """ """
    number_of_teams_league = len(league_data["standings"]["results"])
    return number_of_teams_league


# Get first season data appears
def get_first_Season_year_data(df):
    """ """
    first_Season_year_data = df["season_name"].min()
    first_Season_year_data = first_Season_year_data[0:4]
    return first_Season_year_data


def get_league_name(league_data):
    """ """
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
    """ """
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
