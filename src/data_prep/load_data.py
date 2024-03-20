import pandas as pd
import requests


def get_league_data(league_id):
    """
    
    TBC

    Parameters
    ----------
    league_id : int
        A mini league ID. This can be extracted from the league URL:
        https://fantasy.premierleague.com/leagues/X/standings/c

    Returns
    -------
    team_data : list
        There is one element in this list for each team.
        Each element is a key value pair for the individual teams information.
        This includes team ID, player name etc.
    
    """
    
    url = f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/'
    league_data = requests.get(url)
    league_data = league_data.json()

    team_data = league_data['standings']['results']

    return league_data, team_data


def get_team_history(team_id):
    """
    """
    
    url = f'https://fantasy.premierleague.com/api/entry/{team_id}/history/'
    team_data = requests.get(url)
    team_data = team_data.json()

    team_history = team_data['past']

    return team_history


def get_manager_information(team_id):
    """
    """
    
    url = f'https://fantasy.premierleague.com/api/entry/{team_id}/'
    manager_data = requests.get(url)
    manager_data = manager_data.json()

    summary_overall_rank = manager_data['summary_overall_rank']
    player_region_iso_code_long = manager_data['player_region_iso_code_long']
    favourite_team = manager_data['favourite_team']


    return summary_overall_rank, player_region_iso_code_long, favourite_team


def get_managers_information_league(team_data):
    """
    This loops through each team id in a league and individualy gets the
    information for that team, and adds it to a list.
    """
    manager_information = []
    for team in team_data:
        entry = team['entry']
        (summary_overall_rank, 
        player_region_iso_code_long, 
        favourite_team) = get_manager_information(entry)
        
        manager_information.append(
            {
            "entry": entry,
            "summary_overall_rank": summary_overall_rank,
            "player_region_iso_code_long": player_region_iso_code_long,
            "favourite_team": favourite_team
            }
        )
    return manager_information


def get_league_history(team_data):
    """
    """
    
    league_history = []
    for i in team_data:
        # Get team history for the current team ID
        team_history = get_team_history(i['entry'])

        # Add team ID to history and extend league_history
        for item in team_history:
            item['team_id'] = i['entry']
            item['team_name'] = i['entry_name']
            item['manager_name'] = i['player_name']
        league_history += team_history
    
    return league_history


def get_current_season_information():
    """
    Checks if the current season is complete.
    Gets the general bootstrap-static and all gameweeks data (events).
    Gets the final gameweek and returns the value of the 'finished' binary key.

    Also returns the current season.

    Returns
    -------
    final_gw_finished : bool
        There is one element in this list for each team.
        Each element is a key value pair for the individual teams information.
        This includes team ID, player name etc.
    
    """
    
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    bootstrap_data = requests.get(url)
    bootstrap_data = bootstrap_data.json()

    final_gw_finished = bootstrap_data['events'][-1]['finished']

    year_start = bootstrap_data['events'][0]['deadline_time'][0:4]
    current_season_year = f"{year_start}/{str(int(year_start) + 1)[2:4]}"

    team_ids = pd.DataFrame(bootstrap_data['teams'])[['id','name']]

    return final_gw_finished, current_season_year, team_ids