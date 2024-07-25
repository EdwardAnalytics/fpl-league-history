import requests
import concurrent.futures
import pandas as pd

# Set page limit
page_limit = 10


def fetch_url(url):
    """
    Fetches data from a given URL using the requests library.

    Parameters:
    ----------
    url : str
        The URL to fetch data from.

    Returns:
    ----------
    data : dict or None
        The JSON data retrieved from the URL if the request is successful, otherwise None.
    """
    response = requests.get(url)
    if response.ok:
        data = response.json()
        return data
    else:
        return None


# Function to fetch URLs concurrently
def fetch_urls_concurrently(urls):
    """
    Fetches multiple URLs concurrently using ThreadPoolExecutor.

    Parameters:
    ----------
    urls : list
        A list of URLs to fetch.

    Returns:
    ----------
    results : list:
        A list containing the fetched results from the URLs.
    """
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
    """
    Fetches multiple URLs concurrently using ThreadPoolExecutor.
    Returns the fetched data along with their corresponding URLs.

    Parameters:
    ----------
    urls : list
        A list of URLs to fetch.

    Returns:
    ----------
    results : list
        A list containing dictionaries with URL and fetched data.
    """
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
            current_gamekweek = "Season Not Started"

    year_start = bootstrap_data["events"][0]["deadline_time"][0:4]
    current_season_year = f"{year_start}/{str(int(year_start) + 1)[2:4]}"

    team_ids = pd.DataFrame(bootstrap_data["teams"])[["id", "name"]]

    return final_gw_finished, current_season_year, team_ids, current_gamekweek


def get_league_data_season_started(league_id):
    """
    Retrieves league standings data for a given league ID when the season has started.

    Parameters:
    ----------
    league_id : int
        The ID of the league for which standings data is to be fetched.

    Returns:
    ----------
    league_data : dict
        League data retrieved from the first URL.
    team_data : list
        Team data extracted from all fetched URLs.
    """
    urls = []
    page = 1
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_standings={page}"
    urls.append(url)

    league_data = requests.get(url).json()
    all_results = [league_data]

    while league_data["standings"]["has_next"] == True:
        page += 1

        if page > page_limit:
            break

        url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_standings={page}"
        league_data = requests.get(url).json()
        urls.append(url)
        all_results.append(league_data)

    team_data = []
    for item in all_results:
        if "standings" in item and "results" in item["standings"]:
            team_data.extend(item["standings"]["results"])

    return all_results[0], team_data


def get_league_data_season_not_started(league_id):
    """
    Retrieves league new entries data for a given league ID when the season has not started.

    Parameters:
    ----------
    league_id : int
        The ID of the league for which new entries data is to be fetched.

    Returns:
    ----------
    league_data : dict
        League data retrieved from the first URL.
    team_data : list
        Team data extracted from all fetched URLs.
    """
    urls = []
    page = 1
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_new_entries={page}"
    urls.append(url)

    league_data = requests.get(url).json()
    all_results = [league_data]

    while league_data["new_entries"]["has_next"] == True:
        page += 1

        if page > page_limit:
            break

        url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_new_entries={page}"
        league_data = requests.get(url).json()
        urls.append(url)
        all_results.append(league_data)

    team_data = []
    for item in all_results:
        if "new_entries" in item and "results" in item["new_entries"]:
            team_data.extend(item["new_entries"]["results"])

    for team in team_data:
        team["player_name"] = (
            f"{team.pop('player_first_name')} {team.pop('player_last_name')}"
        )

    return all_results[0], team_data


def get_league_data(league_id):
    """
    Retrieves league data and team data for a given league ID.

    Parameters:
    ----------
    league_id : int
        The ID of the league for which data is to be fetched.

    Returns:
    ----------
    league_data : dict
        League data retrieved from the first URL.
    team_data : list
        Team data extracted from all fetched URLs.
    """
    final_gw_finished, current_season_year, team_ids, current_gamekweek = (
        get_current_season_information()
    )

    if current_gamekweek != "Season Not Started":
        return get_league_data_season_started(league_id)
    else:
        return get_league_data_season_not_started(league_id)


def get_league_urls(league_id):
    """
    Retrieves URLs for fetching league standings data for a given league ID from the Fantasy Premier League API.

    Parameters:
    ----------
    league_id :int
        The ID of the league for which standings URLs are to be fetched.

    Returns:
    ----------
    urls : list
        A list of URLs for fetching league standings data.
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


def get_league_data_from_urls(league_id):
    """
    Retrieves league data and team data for a given league ID.

    Parameters:
    ----------
    league_id : int
        The ID of the league for which data is to be fetched.

    Returns:
    ----------
    league_data : dict
        League data retrieved from the first URL.
    team_data : list
        Team data extracted from all fetched URLs.
    """
    urls = get_league_urls(league_id=league_id)
    all_results = fetch_urls_concurrently(urls=urls)

    team_data = []
    for item in all_results:
        if "standings" in item and "results" in item["standings"]:
            team_data.extend(item["standings"]["results"])

    league_data = all_results[0]
    return league_data, team_data


def get_manager_urls(team_data):
    """
    Retrieves URLs for fetching manager data based on team data.

    Parameters
    ----------
    team_data : list
        A list of dictionaries containing team data.

    Returns
    -------
    list
        A list of URLs for fetching manager data.
    """
    urls = []
    for team in team_data:
        entry = team["entry"]
        url = f"https://fantasy.premierleague.com/api/entry/{entry}/"
        urls.append(url)
    return urls


def get_managers_information_league(team_data):
    """
    Retrieves detailed information about managers in a league based on team data.

    This function takes a list of dictionaries containing team data as input and fetches detailed information
    about each manager associated with the teams. The function first generates URLs for fetching manager data
    using the provided team data. Then, it concurrently fetches data from these URLs using the
    fetch_urls_concurrently function. Finally, it filters and structures the retrieved data to extract
    relevant manager information such as entry ID, overall rank, player's region ISO code, and favourite team.

    Parameters
    ----------
    team_data : list
        A list of dictionaries containing team data, including information about each team in the league.

    Returns
    -------
    manager_information : list
        A list of dictionaries containing filtered information about each manager in the league.
        Each dictionary contains the following keys:
            - 'entry': The unique ID of the manager.
            - 'summary_overall_rank': The overall rank of the manager.
            - 'player_region_iso_code_long': The ISO code of the player's region.
            - 'favourite_team': The favourite team of the manager.
    """
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
    """
    Generates URLs for fetching team history data based on team data.

    Parameters
    ----------
    team_data : list
        A list of dictionaries containing team data.

    Returns
    -------
    list
        A list of URLs for fetching team history data.
    """
    urls = []
    for team in team_data:
        entry = team["entry"]
        url = f"https://fantasy.premierleague.com/api/entry/{entry}/history/"
        urls.append(url)
    return urls


def get_league_history(team_data):
    """
    Retrieves historical data for teams in a league based on team data.

    This function takes a list of dictionaries containing team data as input and fetches historical data
    for each team in the league. It generates URLs for fetching team history data using the provided team data
    and fetches data from these URLs concurrently. Then, it enhances each historical data entry with additional
    information including team ID, team name, and manager name.

    Parameters
    ----------
    team_data : list
        A list of dictionaries containing team data, including information about each team in the league.

    Returns
    -------
    league_history : slist
        A list of dictionaries containing historical data for all teams in the league.
        Each dictionary represents a historical entry and includes the following keys:
            - 'team_id': The unique ID of the team.
            - 'team_name': The name of the team.
            - 'manager_name': The name of the manager.
            - Other historical data keys provided by the Fantasy Premier League API.
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
