import datetime
import pytest
from unittest.mock import MagicMock
from src.app_utility.app_tools import get_most_recent_august_start, remove_starting_the


def test_get_most_recent_august_start(mocker):
    mock_datetime = MagicMock(wraps=datetime.datetime)

    date_after_august = datetime.datetime(2024, 9, 4)
    date_before_august = datetime.datetime(2024, 7, 31)

    mock_datetime.now.return_value = date_after_august
    mocker.patch("datetime.datetime", mock_datetime)
    assert get_most_recent_august_start() == 2024

    mock_datetime.now.return_value = date_before_august
    mocker.patch("datetime.datetime", mock_datetime)
    assert get_most_recent_august_start() == 2023


def test_remove_starting_the():
    # Test cases where 'the' is at the beginning
    assert remove_starting_the("The quick brown fox") == "quick brown fox"
    assert remove_starting_the("the quick brown fox") == "quick brown fox"
    assert remove_starting_the("THE quick brown fox") == "quick brown fox"

    # Test cases where 'the' is not at the beginning
    assert remove_starting_the("quick brown fox") == "quick brown fox"
    assert remove_starting_the("quick the brown fox") == "quick the brown fox"

    # Test cases with no 'the' at all
    assert (
        remove_starting_the("quick brown fox jumps over the lazy dog")
        == "quick brown fox jumps over the lazy dog"
    )

    # Test cases with only 'the' less than 5 characters
    assert remove_starting_the("the") == "the"
    assert remove_starting_the("The") == "The"
    assert remove_starting_the("THE") == "THE"

    # Test cases without 'the' less than 5 characters
    assert remove_starting_the("a") == "a"
    assert remove_starting_the("Dog") == "Dog"
    assert remove_starting_the("CAT") == "CAT"

    # Test cases with only 'the' more than 5 characters
    assert remove_starting_the("the  ") == ""
    assert remove_starting_the("The  ") == ""
    assert remove_starting_the("THE  ") == ""
