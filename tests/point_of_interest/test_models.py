import uuid

import pytest

from point_of_interest.models import POI, HistoricalImportData, SourceType


@pytest.mark.parametrize(
    "data, expected_source, expected_filename",
    [
        (
            {"source": SourceType.CSV[0], "filename": "import_2025_09_03.csv"},
            SourceType.CSV[0],
            "import_2025_09_03.csv",
        )
    ],
)
@pytest.mark.django_db
def test_historical_import_creation(data, expected_source, expected_filename):
    """Unit historical_import_data instance test"""
    obj = HistoricalImportData.objects.create(**data)
    assert isinstance(obj.id, uuid.UUID)
    assert obj.source == expected_source
    assert obj.filename == expected_filename
    assert obj.timestamp is not None


@pytest.mark.parametrize(
    "poi_data, expected_category",
    [
        (
            {
                "external_id": "6166590368",
                "name": "unser Laden, Familie Lackinger",
                "latitude": 48.008273899935716,
                "longitude": 16.2454885,
                "category": "convenience-store",
                "ratings": [2, 2, 3, 3, 4, 5, 2, 2, 4, 1],
                "description": "dzpdfeldblkzqcxltrn",
            },
            "convenience-store",
        )
    ],
)
@pytest.mark.django_db
def test_poi_creation(poi_data, expected_category):
    """Unit poi instance test"""
    poi = POI.objects.create(**poi_data)
    assert isinstance(poi.id, uuid.UUID)
    assert poi.external_id == poi_data["external_id"]
    assert poi.name == poi_data["name"]
    assert poi.category == expected_category
    assert poi.ratings == poi_data["ratings"]
    assert poi.description == poi_data["description"]


@pytest.mark.parametrize(
    "ratings, expected_str",
    [
        ([4, 5, 3], "4.00"),
        ([4, 3.5, 5], "4.17"),
        ([4.2, 4.2], "4.20"),
        ([1.0], "1.00"),
        ([4.25, 4.25], "4.25"),
    ],
)
@pytest.mark.django_db
def test_poi_avg_rating_with_floats(create_poi_instance, ratings, expected_str):
    """test avg_rating property method"""
    create_poi_instance.ratings = ratings
    assert create_poi_instance.avg_rating is not None
    assert create_poi_instance.avg_rating.to_eng_string() == expected_str


@pytest.mark.django_db
def test_poi_avg_rating_empty_is_none(create_poi_instance):
    """test avg_rating property method"""
    create_poi_instance.ratings = []
    assert create_poi_instance.avg_rating is None
