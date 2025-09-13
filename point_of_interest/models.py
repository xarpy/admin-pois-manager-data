from decimal import ROUND_HALF_UP, Decimal
from statistics import mean
from typing import Optional
from uuid import uuid4

from django.db import models

from point_of_interest.enums import SourceType


class HistoricalImportData(models.Model):
    """Historical Import Data model"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    source = models.CharField(max_length=8, choices=SourceType.choices, db_index=True)
    filename = models.CharField(max_length=256, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historical Import Data"
        verbose_name_plural = "Historical Imports Data"
        db_table = "historical_import_data"
        ordering = ["-timestamp"]


class POI(models.Model):
    """Point of Interest model"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="PoI internal ID",
    )
    external_id = models.CharField(
        max_length=128, db_index=True, verbose_name="PoI external ID"
    )
    name = models.CharField(max_length=255, db_index=True, verbose_name="PoI name")
    latitude = models.FloatField()
    longitude = models.FloatField()
    category = models.CharField(
        max_length=64, db_index=True, verbose_name="PoI category"
    )
    ratings = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Point Of Interest"
        verbose_name_plural = "Point Of Interest"
        db_table = "point_of_interest"
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["external_id"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["external_id"], name="unique_external_id")
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"[{self.id}] {self.name} ({self.external_id})"

    @property
    def avg_rating(self) -> float:
        """Returns the average of ratings, limited between 0 and 5, with 2 decimal places."""
        try:
            data = [min(5.0, max(0.0, float(x))) for x in self.ratings]
            return round(sum(data) / len(data), 2) if data else 0.0
        except Exception:
            return 0.0
