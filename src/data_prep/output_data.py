import inflect
import pandas as pd

def filter_rehsaped_season_history(season_start_year, df):
    """
    """
    df[df['season_name'].str[:4].astype(int) >= season_start_year]

    return df


def get_seasons_by_positions(df,position,column_name):
    """"
    """
    df=df[df['league_position']==position].groupby(['team_name','manager_name'])['season_name'].apply(lambda x: ', '.join(map(str, x))).reset_index(name=column_name)

    return df


def get_season_overview(season_history_df_filtered,manager_information,team_ids):
    # Get max value
    max_points_season_index = season_history_df_filtered.groupby('team_name')['total_points'].idxmax()

    # Create a DataFrame with both 'team' and 'ranking' columns for each group
    max_points_season_df = season_history_df_filtered.loc[max_points_season_index, ['team_name', 'manager_name','season_name']]
    max_points_season_df.rename(columns={'season_name': 'max_points_season_year'}, inplace=True)

    # Get max value
    min_rank_season_index = season_history_df_filtered.groupby('team_name')['rank'].idxmin()

    # Create a DataFrame with both 'team' and 'ranking' columns for each group
    min_rank_season_df = season_history_df_filtered.loc[min_rank_season_index, ['team_name','manager_name', 'season_name']]
    min_rank_season_df.rename(columns={'season_name': 'min_rank_season_year'}, inplace=True)

    # Group by 'team' and aggregate values of 'score' column into a string
    seasons_played = season_history_df_filtered.groupby(['team_name','manager_name'])['season_name'].apply(lambda x: ', '.join(map(str, x))).reset_index(name='seasons_played_years')

    seasons_first = get_seasons_by_positions(
        df=season_history_df_filtered,
        position=1,
        column_name='seasons_won_years'
        )

    seasons_second = get_seasons_by_positions(
        df=season_history_df_filtered,
        position=2,
        column_name='seasons_runner_up_years'
        )

    seasons_third = get_seasons_by_positions(
        df=season_history_df_filtered,
        position=3,
        column_name='seasons_third_years'
        )
    
    # Get aggregated stats
    seasons_overview = season_history_df_filtered.groupby(['team_id','team_name','manager_name']).agg(
        seasons_won=('league_position', lambda x: (x == 1).sum()),
        seasons_runner_up=('league_position', lambda x: (x == 2).sum()),
        seasons_third=('league_position', lambda x: (x == 3).sum()),
        seasons_played=('season_name', 'nunique'),
        maximum_points=('total_points', 'max'),
        minimum_rank=('rank', 'min')
    ).reset_index()

    # Join together
    seasons_overview=seasons_overview.merge(
        right=max_points_season_df,
        on=['team_name','manager_name'],
        how='left'
    ).merge(
        right=min_rank_season_df,
        on=['team_name','manager_name'],
        how='left'
    ).merge(
        right=seasons_played,
        on=['team_name','manager_name'],
        how='left'
    ).merge(
        right=seasons_first,
        on=['team_name','manager_name'],
        how='left'
    ).merge(
        right=seasons_second,
        on=['team_name','manager_name'],
        how='left'
    ).merge(
        right=seasons_third,
        on=['team_name','manager_name'],
        how='left'
    ).merge(
        right=pd.DataFrame(manager_information),
        left_on=['team_id'],
        right_on=['entry'],
        how='left'
    ).merge(
        right=team_ids,
        left_on=['favourite_team'],
        right_on=['id'],
        how='left'
    ).sort_values([
        'seasons_won','seasons_runner_up','seasons_third'
    ],ascending=False)

    # Add rank
    seasons_overview['rank']=seasons_overview['seasons_won'].rank(method='min',ascending=False).astype('int')

    return seasons_overview


def get_current_champions(season_history_df_filtered, season_overview):
    """
    """
    current_champions_index = season_history_df_filtered['season_name'].idxmax()

    current_champions_team_name = season_history_df_filtered.loc[current_champions_index, 'team_name']
    current_champions_manager_name = season_history_df_filtered.loc[current_champions_index, 'manager_name']
    current_champions_season_name = season_history_df_filtered.loc[current_champions_index, 'season_name']

    # Get title number and append "st", "nd", "rd" for "1st", "2nd", "3rd" etc.
    title_number = season_overview.loc[season_overview['team_name'] == current_champions_team_name, 'seasons_won']
    p = inflect.engine()
    title_number = p.ordinal(int(title_number))

    current_champions = f"{current_champions_manager_name}: {current_champions_team_name} ({title_number} title) ({current_champions_season_name})"

    return current_champions


def get_most_wins(season_overview):
    """
    """
    most_seasons_won = season_overview['seasons_won'].max()

    most_season_won_teams = season_overview.loc[season_overview['seasons_won'] == most_seasons_won, ['manager_name', 'team_name','seasons_won']].to_dict(orient='records')

    most_season_won_teams_list = []
    for team in most_season_won_teams:
        manager_name = team['manager_name']
        team_name = team['team_name']
        seasons_won = team['seasons_won']
        teams_str = f"{manager_name}: {team_name} ({seasons_won} titles)"
        most_season_won_teams_list.append(teams_str)
    most_season_won_teams_str= "; ".join(most_season_won_teams_list)
    return most_season_won_teams_str


def get_best_rank_points(season_history_df_filtered,column):
    """
    """
    if column == 'rank':
        best = season_history_df_filtered[column].min()
    elif column == 'total_points':
        best = season_history_df_filtered[column].max()    

    best_teams = season_history_df_filtered.loc[season_history_df_filtered[column] == best, ['manager_name', 'team_name','rank','total_points','season_name']].to_dict(orient='records')

    best_teams_list = []
    for team in best_teams:
        manager_name = team['manager_name']
        team_name = team['team_name']
        rank = "{:,}".format(team['rank'])
        total_points = "{:,}".format(team['total_points'])
        season_name = team['season_name']
        teams_str = f"{manager_name}: {team_name}: Rank: {rank}, Points: {total_points} ({season_name})"
        best_teams_list.append(teams_str)
    best_teams_str= "; ".join(best_teams_list)

    return best_teams_str


def aggreagte_season_by_position(position,df,column_name):
    """
    """
    df = df[df['league_position']==position]
    df['Cumulative_Count'] = df.groupby('team_name').cumcount() + 1

    df.loc[:, column_name]  = df['manager_name'] + ': ' + df['team_name'] + ' (' + df['Cumulative_Count'].astype(str) + ')'
    df=df[['season_name',column_name]]

    return df


def get_seasons_by_top_three_teams(season_history_df_filtered):
    """
    """
    champions = aggreagte_season_by_position(position=1,df=season_history_df_filtered,column_name='champions_with_count')
    runners_up = aggreagte_season_by_position(position=2,df=season_history_df_filtered,column_name='runners_up_count')
    third_place = aggreagte_season_by_position(position=3,df=season_history_df_filtered,column_name='third_place_with_count')

    seasons_top_three=champions.merge(
        right=runners_up,
        on='season_name',
        how='left'
    ).merge(
        right=third_place,
        on='season_name',
        how='left'
    ).sort_values(
        by='season_name'
    )

    return seasons_top_three


def get_titles_won_summary(season_overview):
    """
    """
    season_overview.loc[:, 'team']  = season_overview['manager_name'] + ': ' + season_overview['team_name']
    selected_columns=['rank','team','seasons_won','seasons_runner_up','seasons_won_years']
    season_overview = season_overview.loc[(season_overview['seasons_won'] > 0) | (season_overview['seasons_runner_up'] > 0), selected_columns]
    return season_overview