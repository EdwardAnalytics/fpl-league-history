import pytest
import pandas as pd
from src.data_prep.output_league_summary import (
    get_current_champions,
    get_most_wins,
    get_best_rank_points,
    get_number_of_teams_league,
    get_first_Season_year_data,
    get_league_name,
    get_league_summary_kpis,
)


def test_get_current_champions():
    # Sample data for testing
    df = pd.DataFrame(
        {
            "season_name": ["2022/2023", "2023/2024"],
            "team_name": ["Team A", "Team B"],
            "manager_name": ["Manager A", "Manager B"],
        }
    )

    season_overview = pd.DataFrame(
        {"team_name": ["Team A", "Team B"], "seasons_won": [1, 2]}
    )

    # Expected output
    expected_output = "Manager B: Team B (2nd title) (2023/2024)"

    # Test the function
    assert get_current_champions(df, season_overview) == expected_output


def test_get_most_wins():
    # Sample data for testing
    df = pd.DataFrame(
        {
            "manager_name": ["Manager A", "Manager B", "Manager C"],
            "team_name": ["Team A", "Team B", "Team C"],
            "seasons_won": [3, 5, 5],
        }
    )

    # Expected output
    expected_output = "Manager B: Team B (5 titles); Manager C: Team C (5 titles)"

    # Test the function
    assert get_most_wins(df) == expected_output


def test_get_best_rank_points():
    # Sample data for testing
    df = pd.DataFrame(
        {
            "manager_name": ["Manager A", "Manager B", "Manager C"],
            "team_name": ["Team A", "Team B", "Team C"],
            "rank": [1, 2, 1],
            "total_points": [85, 90, 95],
            "season_name": ["2022/2023", "2023/2024", "2021/2022"],
        }
    )

    # Test for best rank
    expected_output_rank = (
        "Manager A: Team A: Rank: 1 (2022/2023); Manager C: Team C: Rank: 1 (2021/2022)"
    )
    assert get_best_rank_points(df, "rank") == expected_output_rank

    # Test for best points
    expected_output_points = "Manager C: Team C: Points: 95 (2021/2022)"
    assert get_best_rank_points(df, "total_points") == expected_output_points


def test_get_number_of_teams_league():
    # Sample data for testing
    team_data = [
        {"team_id": 1, "team_name": "Team A"},
        {"team_id": 2, "team_name": "Team B"},
        {"team_id": 3, "team_name": "Team C"},
    ]

    # Expected output
    expected_output = 3

    # Test the function
    assert get_number_of_teams_league(team_data) == expected_output


def test_get_first_Season_year_data():
    # Sample data for testing
    df = pd.DataFrame({"season_name": ["2022/2023", "2023/2024", "2021/2022"]})

    # Expected output
    expected_output = "2021"

    # Test the function
    assert get_first_Season_year_data(df) == expected_output


def test_get_league_name():
    # Sample data for testing
    league_data = {"league": {"name": "Premier League"}}

    # Expected output
    expected_output = "Premier League"

    # Test the function
    assert get_league_name(league_data) == expected_output


def test_get_league_summary_kpis():
    # Sample data for testing
    first_Season_year_data = "1992"
    number_of_teams_league = 20
    current_champions_output = "Manager A: Team A (3rd title) (2022/2023)"
    most_season_won_teams_str_output = "Manager B: Team B (5 titles)"
    best_points_teams_str_output = "Manager C: Team C: Points: 95 (2021/2022)"
    best_rank_teams_str = "Manager D: Team D: Rank: 1 (2020/2021)"

    # Expected output
    expected_output = pd.DataFrame(
        {
            "Founded": ["1992"],
            "Number of teams": ["20"],
            "Current Champions": ["Manager A: Team A (3rd title) (2022/2023)"],
            "Most Championships": ["Manager B: Team B (5 titles)"],
            "Most Points in a Season": ["Manager C: Team C: Points: 95 (2021/2022)"],
            "Highest Rank in a Season": ["Manager D: Team D: Rank: 1 (2020/2021)"],
        }
    ).T

    # Test the function
    result = get_league_summary_kpis(
        first_Season_year_data,
        number_of_teams_league,
        current_champions_output,
        most_season_won_teams_str_output,
        best_points_teams_str_output,
        best_rank_teams_str,
    )

    pd.testing.assert_frame_equal(result, expected_output)
