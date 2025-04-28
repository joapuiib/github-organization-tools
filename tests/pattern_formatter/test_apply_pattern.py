import pytest
from io import StringIO
from unittest.mock import patch
from ghot.pattern_formatter import PatternFormatter

@pytest.mark.parametrize("pattern,expected", [
    pytest.param(
        "{f0}",
        "brian",
        id="index_0"
    ),
    pytest.param(
        "{f0}.{f1}",
        "brian.COHEN",
        id="combined_index"
    ),
    pytest.param(
        "{name}",
        "brian",
        id="field_name"
    ),
    pytest.param(
        "{name}.{surname}",
        "brian.COHEN",
        id="combined_field_name"
    ),
    pytest.param(
        "{surname.lower()}",
        "cohen",
        id="filter_lower"
    ),
    pytest.param(
        "{name.upper()}",
        "BRIAN",
        id="filter_upper"
    ),
    pytest.param(
        "{name.title()}",
        "Brian",
        id="filter_title"
    ),
    pytest.param(
        "{description.strip()}",
        "An example user",
        id="filter_strip"
    ),
    pytest.param(
        "{description.words(0)}",
        "An",
        id="filter_words_0"
    ),
    pytest.param(
        "{description.words(1)}",
        "example",
        id="filter_words_1"
    ),
    pytest.param(
        "{username.words(1,'-')}",
        "cohen",
        id="filter_words_delimiter"
    ),
    pytest.param(
        "{username.replace('-',' ')}",
        "brian cohen",
        id="filter_replace"
    ),
    pytest.param(
        "{inexisting?}",
        "",
        id="default_value_empty"
    ),
    pytest.param(
        "{inexisting?'name'}",
        "name",
        id="default_value_constant"
    ),
    pytest.param(
        "{inexisting?name}",
        "brian",
        id="default_value_expression"
    ),
    pytest.param(
        "{inexisting.lower()?name}",
        "brian",
        id="default_value_after_filter"
    ),
])
def test_apply_pattern(pattern, expected):
    formatter = PatternFormatter()
    formatter.schema = {
            "name": 0,
            "surname": 1,
            "username": 2,
            "description": 3,
    }

    row = ["brian", "COHEN", "brian-cohen", "An example user "]
    result = formatter.format(pattern, row)

    assert result == expected, f"Expected {expected}, but got {result} for pattern: {pattern}"


def test_apply_invalid_filter():
    formatter = PatternFormatter()
    formatter.schema = {
            "name": 0,
            "surname": 1,
            "username": 2,
            "description": 3,
    }

    row = ["brian", "COHEN", "brian-cohen", "An example user "]
    pattern = "{name.invalid_filter()}"

    with pytest.raises(ValueError, match="Unsupported method 'invalid_filter'"):
        formatter.format(pattern, row)
