from uuid import UUID

from django.contrib import admin
from django.db.models import QuerySet

from point_of_interest.models import POI, HistoricalImportData
from point_of_interest.utils import validate_uuid


@admin.register(HistoricalImportData)
class HistoricalImportDataAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "filename", "timestamp")
    list_filter = ["source"]
    search_fields = ["source"]
    readonly_fields = ["timestamp"]
    list_per_page = 50


@admin.register(POI)
class PointOfInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "external_id", "category", "avg_rating_display")
    list_filter = ["category"]
    search_fields = ("external_id", "name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50

    @admin.display(ordering=None, description="Avg. rating")
    def avg_rating_display(self, obj: POI):
        """Displays the average rating value for the POI instance."""
        return obj.avg_rating

    def get_search_results(self, request, queryset: QuerySet, search_term: str):
        """Search by UUID (internal id) or exact external_id (int), or fallback to default."""
        term_fmt = search_term.strip()
        qs, use_distinct = super().get_search_results(request, queryset, term_fmt)
        if validate_uuid(term_fmt):
            reference_id = UUID(term_fmt)
            qs = queryset.filter(pk=reference_id)
        elif term_fmt.isdigit():
            qs = queryset.filter(external_id=term_fmt)
        return qs, use_distinct
