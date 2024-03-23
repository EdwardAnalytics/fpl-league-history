import pandas as pd


def filter_rehsaped_season_history(season_start_year, df):
    """ """
    df = df[df["season_name"].str[:4].astype(int) >= season_start_year]

    return df


def get_seasons_by_positions(df, position, column_name):
    """ " """
    df = (
        df[df["league_position"] == position]
        .groupby(["team_name", "manager_name"])["season_name"]
        .apply(lambda x: ", ".join(map(str, x)))
        .reset_index(name=column_name)
    )

    return df


def get_season_overview(df, manager_information, team_ids):
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
    """ """
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
    """ """
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
    """ """
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
    """ """
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
