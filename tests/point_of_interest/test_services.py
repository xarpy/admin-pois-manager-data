import pytest

from point_of_interest.services import ImportServiceError, ImportStats
from tests.point_of_interest.conftest import DummyBuilder, ErrorBuilder


def test_import_builder_run_success():
    """Test that the ImportBuilder runs successfully and returns ImportStats."""
    builder = DummyBuilder()
    stats = builder.run()
    assert isinstance(stats, ImportStats)
    assert stats.files_processed == 2
    assert stats.created == 5
    assert stats.updated == 3


def test_import_builder_error():
    """Test that the ImportBuilder raises ImportServiceError on failure."""
    builder = ErrorBuilder(paths=[])
    with pytest.raises(ImportServiceError):
        builder.run()
