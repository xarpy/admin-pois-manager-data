import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from point_of_interest.models import POI, HistoricalImportData, SourceType


@pytest.fixture
def request_factory():
    """Fixture request factory function"""
    return RequestFactory()


@pytest.fixture
@pytest.mark.django_db
def poi_factory():
    """Fixture poi factory function"""

    def _factory(**kwargs):
        data = {
            "external_id": "1234567",
            "name": "Test POI",
            "latitude": 0.0,
            "longitude": 0.0,
            "category": "test",
            "ratings": [],
            "description": "",
        }
        data.update(kwargs)
        return POI.objects.create(**data)

    return _factory


@pytest.fixture
@pytest.mark.django_db
def historical_import_factory():
    """Fixture historical import data factory function"""

    def _factory(**kwargs):
        data = {"source": SourceType.CSV, "filename": "test.csv"}
        data.update(kwargs)
        return HistoricalImportData.objects.create(**data)

    return _factory


@pytest.fixture
@pytest.mark.django_db
def create_user():
    """Fixture responsible to generate a user fixture for tests.
    Returns:
        user: Returns a user instance
    """
    user = User.objects.create_user(
        username="testuser",
        email="test@test.com",
        password="12345",
        is_staff=True,
    )
    return user


@pytest.fixture
@pytest.mark.django_db
def create_poi_instance():
    """Fixture responsible to generate a poi instance.
    Returns:
        POI: Returns a poi instance
    """
    example_data = {
        "external_id": "6166590368",
        "name": "unser Laden, Familie Lackinger",
        "latitude": 48.008273899935716,
        "longitude": 16.2454885,
        "category": "convenience-store",
        "ratings": [2, 2, 3, 3, 4, 5, 2, 2, 4, 1],
        "description": "dzpdfeldblkzqcxltrn",
    }
    instance = POI.objects.create(**example_data)
    return instance


@pytest.fixture
@pytest.mark.django_db
def create_historical_data_instance():
    """Fixture responsible to generate a HistoricalImportData instance.
    Returns:
        HistoricalImportData: Returns a HistoricalImportData instance
    """
    example_data = {"source": SourceType.CSV[0], "filename": "pois.csv"}
    instance = HistoricalImportData.objects.create(**example_data)
    return instance
