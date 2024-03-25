import requests
import concurrent.futures
import pandas as pd


def fetch_url(url):
    response = requests.get(url)
    if response.ok:
        data = response.json()
        return data
    else:
        return None


# Function to fetch URLs concurrently
def fetch_urls_concurrently(urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = [executor.submit(fetch_url, url) for url in urls]

        # Retrieve results as they become available
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results


def fetch_urls_concurrently_with_url(urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = {executor.submit(fetch_url, url): url for url in urls}

        # Retrieve results as they become available
        results = []
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            result = future.result()
            if result:
                # Append the result with its corresponding URL
                result_with_url = {"url": url, "data": result}
                results.append(result_with_url)
    return results


def get_league_urls(league_id):
    """
    Get data for a specific fantasy league from the Premier League Fantasy API.

    Parameters
    ----------
    league_id : int
        The ID of the fantasy league.

    Returns
    -------
    league_data : dict
        A dictionary containing data about the league.
    team_data : list
        A list containing data about the teams in the league.

    """
    # Loop through each page
    urls = []
    page = 1
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_standings={page}"
    urls.append(url)

    league_data = requests.get(url)
    league_data = league_data.json()

    while league_data["standings"]["has_next"] == True:
        page += 1

        url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_standings={page}"

        league_data = requests.get(url)
        league_data = league_data.json()

        urls.append(url)

    return urls


def get_league_data(league_id):
    """ """
    urls = get_league_urls(league_id=league_id)
    all_results = fetch_urls_concurrently(urls=urls)

    team_data = []
    for item in all_results:
        if "standings" in item and "results" in item["standings"]:
            team_data.extend(item["standings"]["results"])

    league_data = all_results[0]
    return league_data, team_data


def get_manager_urls(team_data):
    urls = []
    for team in team_data:
        entry = team["entry"]
        url = f"https://fantasy.premierleague.com/api/entry/{entry}/"
        urls.append(url)
    return urls


def get_managers_information_league(team_data):
    """ """
    urls = get_manager_urls(team_data=team_data)
    all_results = fetch_urls_concurrently(urls=urls)

    manager_information = []
    for dictionary in all_results:
        filtered_dict = {
            "entry": dictionary.get("id"),
            "summary_overall_rank": dictionary.get("summary_overall_rank"),
            "player_region_iso_code_long": dictionary.get(
                "player_region_iso_code_long"
            ),
            "favourite_team": dictionary.get("favourite_team"),
        }
        manager_information.append(filtered_dict)

    return manager_information


def get_team_urls(team_data):
    urls = []
    for team in team_data:
        entry = team["entry"]
        url = f"https://fantasy.premierleague.com/api/entry/{entry}/history/"
        urls.append(url)
    return urls


def get_league_history(team_data):
    """
    TBC
    """

    urls = get_team_urls(team_data=team_data)
    all_results = fetch_urls_concurrently_with_url(urls=urls)

    for result in all_results:
        # Get the URL
        url = result["url"]
        # Extract team_id from URL
        start_index = url.find("entry/") + len("entry/")
        end_index = url.find("/history/")
        team_id = url[start_index:end_index]
        # Add team_id to each dictionary in the 'past' key
        for item in result["data"]["past"]:
            # Find the corresponding team data
            for team in team_data:
                if team["entry"] == int(team_id):
                    # Add team_name and manager_name to the dictionary
                    item["team_id"] = int(team_id)
                    item["team_name"] = team["entry_name"]
                    item["manager_name"] = team["player_name"]
                    break

    # Extract 'past' dictionaries into one big list
    league_history = [item for result in all_results for item in result["data"]["past"]]

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

    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    bootstrap_data = requests.get(url)
    bootstrap_data = bootstrap_data.json()

    final_gw_finished = bootstrap_data["events"][-1]["finished"]

    # Get Current gameweek
    for event in bootstrap_data["events"]:
        if event["is_current"] == True:
            current_gamekweek = event["id"]
        else:
            pass

    year_start = bootstrap_data["events"][0]["deadline_time"][0:4]
    current_season_year = f"{year_start}/{str(int(year_start) + 1)[2:4]}"

    team_ids = pd.DataFrame(bootstrap_data["teams"])[["id", "name"]]

    return final_gw_finished, current_season_year, team_ids, current_gamekweek
