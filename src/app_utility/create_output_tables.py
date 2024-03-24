import pandas as pd

from src.data_prep.load_data import (
    get_league_data,
    get_league_history,
    get_current_season_information,
    get_managers_information_league,
)
from src.data_prep.reshape_data import (
    summarise_season_current,
    summarise_season_history,
)
from src.data_prep.output_league_season_current import reformat_season_current
from src.data_prep.output_league_seasons_history import (
    filter_rehsaped_season_history,
    get_season_overview,
    get_seasons_by_top_three_teams,
    get_titles_won_summary,
    reformat_season_overview,
    reformat_season_history,
    get_all_time_table,
)

from src.data_prep.output_league_summary import (
    get_current_champions,
    get_most_wins,
    get_best_rank_points,
    get_number_of_teams_league,
    get_first_Season_year_data,
    get_league_name,
    get_league_summary_kpis,
)

import time


def get_team_and_league_data(league_id):
    league_data, team_data = get_league_data(league_id=league_id)
    print("get_league_data")
    manager_information = get_managers_information_league(team_data=team_data)
    print("get_managers_information_league")
    season_history = get_league_history(team_data=team_data)
    print("season_history")
    final_gw_finished, current_season_year, team_ids, current_gamekweek = (
        get_current_season_information()
    )
    
    print("get_current_season_information")

    season_current_df = summarise_season_current(
        league_data=league_data,
        team_data=team_data,
        manager_information=manager_information,
        current_season_year=current_season_year,
        team_ids=team_ids,
    )
    
    print("summarise_season_current")

    season_history_df = summarise_season_history(
        season_history=season_history,
        season_current_df=season_current_df,
        final_gw_finished=final_gw_finished,
    )
    
    print("summarise_season_history")

    return (
        league_data,
        manager_information,
        team_ids,
        final_gw_finished,
        season_history,
        season_current_df,
        season_history_df,
        current_gamekweek,
        team_data,
    )


def get_team_and_league_data_filtered_summarised(
    league_data,
    manager_information,
    team_ids,
    season_current_df,
    season_history_df,
    season_start_year,
    team_data,
):
    season_history_df_filtered = filter_rehsaped_season_history(
        season_start_year=season_start_year, df=season_history_df
    )
    
    print("filter_rehsaped_season_history")
    season_overview = get_season_overview(
        df=season_history_df_filtered,
        manager_information=manager_information,
        team_ids=team_ids,
    )
    
    print("get_season_overview")

    current_champions_output = get_current_champions(
        df=season_history_df_filtered, season_overview=season_overview
    )
    
    print("get_current_champions")
    most_season_won_teams_str_output = get_most_wins(df=season_overview)
    best_rank_teams_str = get_best_rank_points(
        df=season_history_df_filtered, column="rank"
    )
    
    print("get_most_wins")
    best_points_teams_str_output = get_best_rank_points(
        df=season_history_df_filtered, column="total_points"
    )
    
    print("get_best_rank_points")
    number_of_teams_league = get_number_of_teams_league(team_data=team_data)
    
    print("get_number_of_teams_league")
    first_Season_year_data = get_first_Season_year_data(df=season_history_df_filtered)
    
    print("get_first_Season_year_data")

    league_name = get_league_name(league_data=league_data)
    
    print("get_league_name")
    league_summary_kpis = get_league_summary_kpis(
        first_Season_year_data=first_Season_year_data,
        number_of_teams_league=number_of_teams_league,
        current_champions_output=current_champions_output,
        most_season_won_teams_str_output=most_season_won_teams_str_output,
        best_points_teams_str_output=best_points_teams_str_output,
        best_rank_teams_str=best_rank_teams_str,
    )
    
    print("get_league_summary_kpis")

    seasons_top_three_output = get_seasons_by_top_three_teams(
        df=season_history_df_filtered
    )
    
    print("get_seasons_by_top_three_teams")
    titles_won_summary_output = get_titles_won_summary(df=season_overview)
    season_overview_output = reformat_season_overview(df=season_overview)
    season_current_df_output = reformat_season_current(df=season_current_df)
    season_history_df_output = reformat_season_history(df=season_history_df_filtered)
    all_time_table_output = get_all_time_table(df=season_history_df_filtered)
    
    print("get_all_time_table")

    return (
        league_name,
        league_summary_kpis,
        seasons_top_three_output,
        titles_won_summary_output,
        season_overview_output,
        season_current_df_output,
        season_history_df_output,
        all_time_table_output,
    )
