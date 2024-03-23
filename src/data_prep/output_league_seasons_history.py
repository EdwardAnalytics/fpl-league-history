import pandas as pd


def filter_rehsaped_season_history(season_start_year, df):
    """
    Filter the reshaped season history DataFrame based on a given start year.

    Parameters
    ----------
    season_start_year : int
        The start year of the seasons to include.
    df : pandas.DataFrame
        The reshaped season history DataFrame.

    Returns
    -------
    df: pandas.DataFrame
        The filtered DataFrame containing season history.

    """
    df = df[df["season_name"].str[:4].astype(int) >= season_start_year]

    return df


def get_seasons_by_positions(df, position, column_name):
    """
    Get seasons won, runners-up, or third-place finish for each team.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing season data.
    position : int
        The position to filter the data by.
    column_name : str
        The name of the column to store the result.

    Returns
    -------
    df : pandas.DataFrame
        A DataFrame containing seasons won, runners-up, or third-place finishes for each team.

    """
    df = (
        df[df["league_position"] == position]
        .groupby(["team_name", "manager_name"])["season_name"]
        .apply(lambda x: ", ".join(map(str, x)))
        .reset_index(name=column_name)
    )

    return df


def get_season_overview(df, manager_information, team_ids):
    """
    Generate an overview of the performance of teams across seasons.

    This function aggregates various statistics for each team across seasons, including the number of times they won, were runners-up or finished third, the total number of seasons played, the maximum points achieved in a season, the minimum rank attained in a season, and more.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing data about teams' performances across seasons.
    manager_information : list
        Information about managers for all teams in the league.
    team_ids : pandas.DataFrame
        DataFrame containing team IDs and corresponding team names.

    Returns
    -------
    seasons_overview : pandas.DataFrame
        A DataFrame summarizing the performance of teams across seasons, including aggregated statistics.

    """
    # Get max value
    max_points_season_index = df.groupby("team_name")["total_points"].idxmax()

    # Create a DataFrame with both 'team' and 'ranking' columns for each group
    max_points_season_df = df.loc[
        max_points_season_index, ["team_name", "manager_name", "season_name"]
    ]
    max_points_season_df.rename(
        columns={"season_name": "max_points_season_year"}, inplace=True
    )

    # Get max value
    min_rank_season_index = df.groupby("team_name")["rank"].idxmin()

    # Create a DataFrame with both 'team' and 'ranking' columns for each group
    min_rank_season_df = df.loc[
        min_rank_season_index, ["team_name", "manager_name", "season_name"]
    ]
    min_rank_season_df.rename(
        columns={"season_name": "min_rank_season_year"}, inplace=True
    )

    # Group by 'team' and aggregate values of 'score' column into a string
    seasons_played = (
        df.groupby(["team_name", "manager_name"])["season_name"]
        .apply(lambda x: ", ".join(map(str, x)))
        .reset_index(name="seasons_played_years")
    )

    seasons_first = get_seasons_by_positions(
        df=df, position=1, column_name="seasons_won_years"
    )

    seasons_second = get_seasons_by_positions(
        df=df, position=2, column_name="seasons_runner_up_years"
    )

    seasons_third = get_seasons_by_positions(
        df=df, position=3, column_name="seasons_third_years"
    )

    # Get aggregated stats
    seasons_overview = (
        df.groupby(["team_id", "team_name", "manager_name"])
        .agg(
            seasons_won=("league_position", lambda x: (x == 1).sum()),
            seasons_runner_up=("league_position", lambda x: (x == 2).sum()),
            seasons_third=("league_position", lambda x: (x == 3).sum()),
            seasons_played=("season_name", "nunique"),
            maximum_points=("total_points", "max"),
            minimum_rank=("rank", "min"),
        )
        .reset_index()
    )

    # Join together
    seasons_overview = (
        seasons_overview.merge(
            right=max_points_season_df, on=["team_name", "manager_name"], how="left"
        )
        .merge(right=min_rank_season_df, on=["team_name", "manager_name"], how="left")
        .merge(right=seasons_played, on=["team_name", "manager_name"], how="left")
        .merge(right=seasons_first, on=["team_name", "manager_name"], how="left")
        .merge(right=seasons_second, on=["team_name", "manager_name"], how="left")
        .merge(right=seasons_third, on=["team_name", "manager_name"], how="left")
        .merge(
            right=pd.DataFrame(manager_information),
            left_on=["team_id"],
            right_on=["entry"],
            how="left",
        )
        .merge(right=team_ids, left_on=["favourite_team"], right_on=["id"], how="left")
        .sort_values(
            ["seasons_won", "seasons_runner_up", "seasons_third"], ascending=False
        )
    )

    # Add rank
    seasons_overview["rank"] = (
        seasons_overview["seasons_won"]
        .rank(method="min", ascending=False)
        .astype("int")
    )

    return seasons_overview


def aggreagte_season_by_position(position, df, column_name):
    """
    Aggregate seasons based on the finishing position of teams.

    This function filters the DataFrame to include only the teams that finished in the specified position across seasons. It then assigns a cumulative count to each appearance of a team in that position and creates a new column with the manager's name, team name, and cumulative count.



    Parameters
    ----------
    position : int
        The position to filter the data by.
    df : pandas.DataFrame
        The DataFrame containing season data.
    column_name : str
        The name of the column to store the result.

    Returns
    -------
    df : pandas.DataFrame
        A DataFrame containing aggregated season data by position.

    """
    df = df[df["league_position"] == position]
    df["Cumulative_Count"] = df.groupby("team_name").cumcount() + 1

    df.loc[:, column_name] = (
        df["manager_name"]
        + ": "
        + df["team_name"]
        + " ("
        + df["Cumulative_Count"].astype(str)
        + ")"
    )
    df = df[["season_name", column_name]]

    return df


def get_seasons_by_top_three_teams(df):
    """
    Generate an overview of seasons focusing on the top three performing teams.

    This function aggregates information about the seasons where teams finished in the top three positions (champions, runners-up, and third place). It provides a summary of the number of times each team achieved these positions across seasons.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing data about teams' performances across seasons.

    Returns
    -------
    seasons_top_three : pandas.DataFrame
        A DataFrame summarizing the performance of top three teams across seasons.

    """
    champions = aggreagte_season_by_position(
        position=1, df=df, column_name="champions_with_count"
    )
    runners_up = aggreagte_season_by_position(
        position=2, df=df, column_name="runners_up_count"
    )
    third_place = aggreagte_season_by_position(
        position=3, df=df, column_name="third_place_with_count"
    )

    seasons_top_three = (
        champions.merge(right=runners_up, on="season_name", how="left")
        .merge(right=third_place, on="season_name", how="left")
        .sort_values(by="season_name")
    )
    rename_columns = {
        "season_name": "Season",
        "champions_with_count": "Champions (number of titles)",
        "runners_up_count": "Runners-up",
        "third_place_with_count": "Third Place",
    }
    seasons_top_three = seasons_top_three.rename(columns=rename_columns)

    # Fill nulls
    seasons_top_three = seasons_top_three.fillna("")

    return seasons_top_three


def get_titles_won_summary(df):
    """
    Generate a summary of titles won by teams.

    This function filters the DataFrame to include only teams that have won titles or finished as runners-up across seasons. It provides a summary of the number of titles won, number of times finishing as runners-up, and the seasons in which these achievements occurred.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing data about teams' performances across seasons.

    Returns
    -------
    df : pandas.DataFrame
        A DataFrame summarizing the titles won by teams.

    """
    df.loc[:, "team"] = df["manager_name"] + ": " + df["team_name"]
    selected_columns = [
        "rank",
        "team",
        "seasons_won",
        "seasons_runner_up",
        "seasons_won_years",
    ]
    df = df.loc[
        (df["seasons_won"] > 0) | (df["seasons_runner_up"] > 0), selected_columns
    ]

    rename_columns = {
        "rank": "Rank",
        "team": "Team",
        "seasons_won": "Winners",
        "seasons_runner_up": "Runners-up",
        "seasons_won_years": "Winning Seasons",
    }
    df = df.rename(columns=rename_columns)

    # Fill nulls
    df = df.fillna("")

    return df


def reformat_season_overview(df):
    """
    Reformat the season overview DataFrame.

    This function renames columns, formats certain columns, and transposes the DataFrame for better presentation.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the season overview information.

    Returns
    -------
    df : pandas.DataFrame
        A reformatted DataFrame presenting season overview information.

    """
    rename_columns = {
        "manager_name": "Manager",
        "team_name": "Team",
        "seasons_won": "Winners",
        "seasons_won_years": "Winning Seasons",
        "seasons_runner_up": "Runners-up",
        "seasons_runner_up_years": "Runner-up Seasons",
        "seasons_third": "Third",
        "seasons_third_years": "Third Seasons",
        "seasons_played": "Total Seasons Played",
        "seasons_played_years": "Seasons Played",
        "maximum_points": "Best Points in a Season",
        "minimum_rank": "Best Rank in a Season",
        "name": "Favourite Team",
        "player_region_iso_code_long": "Nationality",
    }
    df = df.rename(columns=rename_columns)

    df["Best Points in a Season"] = (
        df["Best Points in a Season"].map("{:,.0f}".format)
        + " ("
        + df["max_points_season_year"]
        + ")"
    )
    df["Best Rank in a Season"] = (
        df["Best Rank in a Season"].map("{:,.0f}".format)
        + " ("
        + df["min_rank_season_year"]
        + ")"
    )

    # Re order columns
    df = df[list(rename_columns.values())]

    # Transpose
    df = df.T

    # Fill nulls
    df = df.fillna("")

    return df


def reformat_season_history(df):
    """
    Reformat the season history DataFrame.

    This function renames columns, formats certain columns, and reorders columns for better presentation.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the season history information.

    Returns
    -------
    df : pandas.DataFrame
        A reformatted DataFrame presenting season history information.

    """
    rename_columns = {
        "season_name": "Season",
        "league_position": "Pos",
        "manager_name": "Manager",
        "team_name": "Team",
        "total_points": "Total Points",
        "rank": "Overall Rank",
    }
    df = df.rename(columns=rename_columns)

    df["Total Points"] = df["Total Points"].map("{:,.0f}".format)
    df["Overall Rank"] = df["Overall Rank"].map("{:,.0f}".format)

    # Re order columns
    df = df[list(rename_columns.values())]

    return df


def get_all_time_table(df):
    """
    Generate an all-time table summarizing performance across seasons.

    This function calculates an all-time table summarising the total points, average points, total seasons played,
    and average rank for each manager and team combination.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing historical performance data across seasons.

    Returns
    -------
    all_time_table : pandas.DataFrame
        A DataFrame representing the all-time table, including columns for Manager, Team, Total Points, Average Points,
        Total Seasons Played, and Average Rank, sorted by Total Points in descending order.
    """
    all_time_table = (
        df.groupby(["manager_name", "team_name"])
        .agg(
            {
                "total_points": ["sum", "mean"],
                "season_name": "nunique",
                "rank": "mean",
            }
        )
        .reset_index()
    )

    all_time_table.columns = [
        "Manager",
        "Team",
        "Total Points",
        "Average Points",
        "Total Seasons Played",
        "Average Rank",
    ]

    all_time_table["Total Points"] = all_time_table["Total Points"].map(
        "{:,.0f}".format
    )
    all_time_table["Average Points"] = all_time_table["Average Points"].map(
        "{:,.0f}".format
    )
    all_time_table["Average Rank"] = all_time_table["Average Rank"].map(
        "{:,.0f}".format
    )

    all_time_table = all_time_table.sort_values(by="Total Points", ascending=False)

    return all_time_table
