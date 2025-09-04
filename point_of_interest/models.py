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
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"[{self.id}] {self.name} ({self.external_id})"

    @property
    def avg_rating(self) -> Optional[Decimal]:
        """Method responsible to calculate the rating average.
        Returns:
            Optional[Decimal]: Return a average result in decimals
        """
        result = None
        rating_data = [float(rating) for rating in self.ratings]
        if rating_data:
            result = Decimal(mean(rating_data)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return result
