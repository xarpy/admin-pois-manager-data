import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

import pandas as pd
from django.db import transaction

from point_of_interest.enums import SourceType
from point_of_interest.exceptions import ImportServiceError
from point_of_interest.models import POI, HistoricalImportData
from point_of_interest.schemas import ImportStats
from point_of_interest.utils import (
    batched,
    iter_xml_dicts,
    normalize_record,
    source_from_path,
)


class ImportBuilder:
    """Imports PoIs from CSV, JSON or XML files, performing batch upserts."""

    def __init__(
        self,
        paths: Sequence[str | Path],
        *,
        chunksize: int = 100_000,
        batch_size: int = 10_000,
    ) -> None:
        self.paths = [Path(p) for p in paths]
        self.chunksize = int(chunksize)
        self.batch_size = int(batch_size)

    def run(self) -> ImportStats:
        """Runs the import process for all provided files."""
        stats = ImportStats()
        for path in self.paths:
            try:
                completed, updated = self._process_file(path)
                stats.created += completed
                stats.updated += updated
                stats.files_processed += 1
                HistoricalImportData.objects.create(
                    source=source_from_path(path),
                    filename=path.name,
                )
            except FileNotFoundError as error:
                raise ImportServiceError(f"File not found: '{path}'") from error
            except (ValueError, KeyError, TypeError) as error:
                raise ImportServiceError(
                    f"Invalid data or format in '{path}': {error}"
                ) from error
        return stats

    def _process_file(self, path: Path) -> tuple[int, int]:
        """Processes a single file and returns (created, updated)."""
        created = 0
        updated = 0
        source = source_from_path(path)
        match source:
            case SourceType.CSV:
                for df in pd.read_csv(path, chunksize=self.chunksize):
                    rows = [
                        normalize_record(row, source)
                        for row in df.to_dict(orient="records")
                    ]
                    c, u = self._upsert_rows(rows)
                    created += c
                    updated += u
                return created, updated
            case SourceType.JSON:
                try:
                    for df in pd.read_json(path, lines=True, chunksize=self.chunksize):
                        rows = [
                            normalize_record(row, source)
                            for row in df.to_dict(orient="records")
                        ]
                        c, u = self._upsert_rows(rows)
                        created += c
                        updated += u
                    return created, updated
                except ValueError:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        data = [data]
                    for chunk in batched(data, self.chunksize):
                        rows = [normalize_record(row, source) for row in chunk]
                        c, u = self._upsert_rows(rows)
                        created += c
                        updated += u
                    return created, updated
            case SourceType.XML:
                buffer = []
                for raw in iter_xml_dicts(path):
                    buffer.append(normalize_record(raw, source))
                    if len(buffer) >= self.chunksize:
                        c, u = self._upsert_rows(buffer)
                        created += c
                        updated += u
                        buffer = []
                if buffer:
                    c, u = self._upsert_rows(buffer)
                    created += c
                    updated += u
                return created, updated
            case _:
                if not path.exists():
                    raise FileNotFoundError(path)
                else:
                    raise ImportServiceError(f"Unsupported file type: {path}")

    @transaction.atomic
    def _upsert_rows(self, rows: List[Dict[str, Any]]) -> tuple[int, int]:
        """Performs upsert of records in the database. Returns (created, updated)."""
        created = 0
        updated = 0
        if rows:
            externals = [r["external_id"] for r in rows]
            current = {
                instance.external_id: instance
                for instance in POI.objects.filter(external_id__in=externals)
            }

            to_create = []
            to_update = []

            for r in rows:
                existing = current.get(r["external_id"])
                if existing:
                    existing.name = r["name"]
                    existing.latitude = r["latitude"]
                    existing.longitude = r["longitude"]
                    existing.category = r["category"]
                    existing.ratings = r["ratings"]
                    existing.description = r["description"]
                    to_update.append(existing)
                else:
                    to_create.append(POI(**r))

            for chunk in batched(to_create, self.batch_size):
                POI.objects.bulk_create(list(chunk), batch_size=self.batch_size)
                created += len(chunk)

            for chunk in batched(to_update, self.batch_size):
                if not chunk:
                    continue
                POI.objects.bulk_update(
                    list(chunk),
                    fields=[
                        "name",
                        "latitude",
                        "longitude",
                        "category",
                        "ratings",
                        "description",
                    ],
                    batch_size=self.batch_size,
                )
                updated += len(chunk)

        return (created, updated)
