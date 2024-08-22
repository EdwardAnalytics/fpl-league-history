import pandas as pd


def get_team_plot_history(df, team, value_to_plot):
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


def get_league_plot_history(df, teams, value_to_plot):
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
            df_plot = get_team_plot_history(
                df, team=teams[0], value_to_plot=value_to_plot
            )
        else:
            df_stage = get_team_plot_history(
                df, team=teams[i], value_to_plot=value_to_plot
            )
            df_plot = pd.merge(df_plot, df_stage, on="Season", how="outer")
    return df_plot
