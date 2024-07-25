import pandas as pd


def summarise_season_current(
    league_data, team_data, manager_information, current_season_year, team_ids
):
    """
    Summarise the current season's data into a DataFrame, performing joins with manager information and team IDs.

    Parameters
    ----------
    league_data : dict
        Data about the league.
    team_data : list
        Data about the teams in the league.
    manager_information : list
        Information about managers for all teams in the league.
    current_season_year : int
        The current season year.
    team_ids : pandas.DataFrame
        DataFrame containing team IDs and corresponding team names.

    Returns
    -------
    season_current_df: pandas.DataFrame
        A DataFrame summarizing the current season's data.

    """
    # Convert to DataFrame
    manager_information_df = pd.DataFrame(manager_information)
    season_current_df = pd.DataFrame.from_dict(team_data)

    # Join with current manager information
    season_current_df = season_current_df.merge(
        right=manager_information_df, how="inner", left_on="entry", right_on="entry"
    )

    # Append Team Supported
    season_current_df = season_current_df.merge(
        right=team_ids, how="left", left_on="favourite_team", right_on="id"
    )

    # Replace NaN with '-' for managers who have not specified a favourite team
    season_current_df["name"] = season_current_df["name"].fillna("-")

    # Match current and previous season schemas
    season_current_df["season_name"] = current_season_year
    rename_columns = {
        "total": "total_points",
        "entry_name": "team_name",
        "player_name": "manager_name",
        "rank": "league_position",
        "id_x": "team_id",
        "entry": "team_id",
    }
    season_current_df = season_current_df.rename(columns=rename_columns)

    # Rename/tidy columns further
    rename_columns = {
        "player_region_iso_code_long": "nationality",
        "summary_overall_rank": "rank",
        "name": "favourite_team_name",
    }
    season_current_df = season_current_df.rename(columns=rename_columns)

    # Pre season check:
    # List of required columns
    required_columns = ["total_points", "rank", "league_position"]

    # Check and create columns with 0s if they don't exist
    for column in required_columns:
        if column not in season_current_df.columns:
            season_current_df[column] = 0

    columns_to_output = [
        "season_name",
        "total_points",
        "rank",
        "team_id",
        "team_name",
        "manager_name",
        "league_position",
        "nationality",
        "favourite_team",
    ]

    season_current_df = season_current_df[columns_to_output]

    return season_current_df


def summarise_season_history(season_history):
    """
    Summarize the historical season data into a DataFrame, ranking the seasons.

    Parameters
    ----------
    season_history : dict
        Data about previous seasons.

    Returns
    -------
    season_history_df: pandas.DataFrame
        A DataFrame summarizing the historical season data.

    """
    # Rank current season
    season_history_df = pd.DataFrame.from_dict(season_history)

    # Rank season data
    season_history_df["league_position"] = (
        season_history_df.groupby("season_name")["rank"]
        .rank(ascending=True)
        .astype(dtype=int)
    )

    season_history_df.sort_values(by=["season_name", "league_position"])

    # Sort output
    season_history_df = season_history_df.sort_values(
        ["season_name", "league_position"], ignore_index=True
    )

    return season_history_df
