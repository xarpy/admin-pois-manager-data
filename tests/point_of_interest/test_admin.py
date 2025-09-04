import uuid
from decimal import Decimal

import pytest
from django.contrib import admin

from point_of_interest.admin import HistoricalImportDataAdmin, PointOfInterestAdmin
from point_of_interest.models import POI, HistoricalImportData


def test_admin_registration():
    assert POI in admin.site._registry
    assert HistoricalImportData in admin.site._registry
    assert isinstance(admin.site._registry[POI], PointOfInterestAdmin)
    assert isinstance(
        admin.site._registry[HistoricalImportData], HistoricalImportDataAdmin
    )


@pytest.mark.parametrize(
    "list_display, list_filter, search_fields, readonly_fields, per_page",
    [
        (
            ("id", "source", "filename", "timestamp"),
            ["source"],
            ["source"],
            ["timestamp"],
            50,
        )
    ],
)
def test_historical_import_admin_config(
    list_display, list_filter, search_fields, readonly_fields, per_page
):
    adm = HistoricalImportDataAdmin(HistoricalImportData, admin.site)
    assert adm.list_display == list_display
    assert adm.list_filter == list_filter
    assert adm.search_fields == search_fields
    assert adm.readonly_fields == readonly_fields
    assert adm.list_per_page == per_page


@pytest.mark.parametrize(
    "list_display, list_filter, search_fields, readonly_fields, per_page",
    [
        (
            ("id", "name", "external_id", "category", "avg_rating_display"),
            ["category"],
            ("external_id", "name"),
            ("created_at", "updated_at"),
            50,
        )
    ],
)
def test_poi_admin_config(
    list_display, list_filter, search_fields, readonly_fields, per_page
):
    adm = PointOfInterestAdmin(POI, admin.site)
    assert adm.list_display == list_display
    assert adm.list_filter == list_filter
    assert adm.search_fields == search_fields
    assert adm.readonly_fields == readonly_fields
    assert adm.list_per_page == per_page


@pytest.mark.parametrize(
    "ratings, expected",
    [
        ([4, 5, 3], Decimal("4.00")),
        ([4, 3.5, 5], Decimal("4.17")),
        ([4.2, 4.2], Decimal("4.20")),
        ([], None),
    ],
)
@pytest.mark.django_db
def test_poi_admin_avg_rating_display(poi_factory, ratings, expected):
    poi = poi_factory(ratings=ratings)
    adm = PointOfInterestAdmin(POI, admin.site)
    assert adm.avg_rating_display(poi) == expected


@pytest.mark.parametrize(
    "search_term, expected_count, expected_name",
    [
        ("1234", 1, "Test One"),
        ("5678", 1, "Test Two"),
    ],
)
@pytest.mark.django_db
def test_poi_admin_search_non_uuid_matches_super(
    request_factory, poi_factory, search_term, expected_count, expected_name
):
    poi_factory(external_id="1234", name="Test One")
    poi_factory(external_id="5678", name="Test Two")
    adm = PointOfInterestAdmin(POI, admin.site)
    request = request_factory.get("/admin/point_of_interest/poi/")
    qs, use_distinct = adm.get_search_results(request, POI.objects.all(), search_term)
    assert qs.count() == expected_count
    assert qs.first().name == expected_name


@pytest.mark.parametrize("use_existing", [True, False])
@pytest.mark.django_db
def test_poi_admin_search_by_valid_uuid_filters_pk(
    request_factory, poi_factory, use_existing
):
    obj = poi_factory(external_id="1234", name="One")
    poi_factory(external_id="5678", name="Two")

    adm = PointOfInterestAdmin(POI, admin.site)
    request = request_factory.get("/admin/point_of_interest/poi/")

    search_term = str(obj.id) if use_existing else str(uuid.uuid4())
    qs, use_distinct = adm.get_search_results(request, POI.objects.all(), search_term)

    if use_existing:
        assert list(qs.values_list("id", flat=True)) == [obj.id]
    else:
        assert qs.count() == 0
