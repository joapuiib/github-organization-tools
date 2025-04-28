import pytest
from io import StringIO
from unittest.mock import patch
from ghot.pattern_formatter import PatternFormatter

@pytest.mark.parametrize("field_name,expected", [
    pytest.param(
        "id",
        "user.id",
        id="field_name"
    ),
    pytest.param(
        "username",
        "user.username",
        id="field_name_2"
    ),
    pytest.param(
        "f0",
        "user.id",
        id="index_0"
    ),
    pytest.param(
        "f1",
        "user.username",
        id="index_1"
    ),
])
def test_resolve_field(field_name, expected):
    formatter = PatternFormatter()
    formatter.schema = {
        "id": 0,
        "username": 1,
        "repo": 2,
    }

    row = ["user.id", "user.username", "user-repo"]
    result = formatter.resolve_field(field_name, row)

    assert result == expected, f"Expected {expected}, but got {result} for field_name: {field_name}"



@pytest.mark.parametrize("field_name,expected", [
    pytest.param(
        "not_a_field",
        "not found in schema",
        id="not_a_field"
    ),
    pytest.param(
        "f5",
        "out of range",
        id="index_out_of_bounds"
    ),
])
def test_resolve_field_error(field_name, expected):
    formatter = PatternFormatter()
    formatter.schema = {
        "id": 0,
        "username": 1,
        "repo": 2,
    }

    row = ["user.id", "user.username", "user-repo"]

    with pytest.raises(ValueError, match=expected):
        formatter.resolve_field(field_name, row)

