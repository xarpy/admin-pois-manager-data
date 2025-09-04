from uuid import uuid4

import pytest

from point_of_interest.utils import validate_uuid


@pytest.mark.parametrize(
    "uuid_str, expected",
    [
        (str(uuid4()), True),
        ("test", False),
    ],
)
def test_validate_uuid(uuid_str, expected):
    """Test validate_uuid function"""
    result = validate_uuid(uuid_str)
    assert result == expected
