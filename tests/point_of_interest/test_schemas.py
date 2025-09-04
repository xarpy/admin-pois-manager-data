from point_of_interest.schemas import ImportData, ImportStats


def test_import_stats():
    stats = ImportStats(files_processed=1, created=2, updated=3)
    assert stats.files_processed == 1
    assert stats.created == 2
    assert stats.updated == 3


def test_import_data_creation():
    """Test the creation of the ImportData dataclass."""
    data = ImportData(
        external_id="E1",
        name="Praça Central",
        latitude=-23.55,
        longitude=-46.63,
        category="Parque",
        ratings=[4.5, 5.0, 3.8],
        description="Local agradável",
    )
    assert data.external_id == "E1"
    assert data.name == "Praça Central"
    assert data.latitude == -23.55
    assert data.ratings == [4.5, 5.0, 3.8]
    assert data.description == "Local agradável"


def test_import_data_to_dict():
    """Test the to_dict method of the ImportData dataclass."""
    data = ImportData(
        external_id="E2",
        name="Museu",
        latitude=10.0,
        longitude=20.0,
        category="Cultura",
        ratings=[4.0],
        description="Museu histórico",
    )
    d = data.to_dict()
    assert isinstance(d, dict)
    assert d["external_id"] == "E2"
    assert d["name"] == "Museu"
    assert d["ratings"] == [4.0]


def test_parse_ratings():
    """Test the _parse_ratings method with various input formats."""
    assert ImportData._parse_ratings([1, 2, 3]) == [1.0, 2.0, 3.0]
    assert ImportData._parse_ratings("4.5,5,3.8") == [4.5, 5.0, 3.8]
    assert ImportData._parse_ratings("[1,2,3]") == [1.0, 2.0, 3.0]
    assert ImportData._parse_ratings(5) == [5.0]
    assert ImportData._parse_ratings("") == []
    assert ImportData._parse_ratings(None) == []
