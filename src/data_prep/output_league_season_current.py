import pandas as pd


def reformat_season_current(df):
    rename_columns = {
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
