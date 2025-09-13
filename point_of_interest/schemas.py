import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from point_of_interest.enums import SourceType


@dataclass(slots=True)
class ImportStats:
    """ImportStats dataclasses representing statistics about the import process."""

    files_processed: int = 0
    created: int = 0
    updated: int = 0


@dataclass(slots=True)
class ImportData:
    """ImportData dataclasses representing a normalized PoI record."""

    external_id: str
    name: str
    latitude: float
    longitude: float
    category: str
    ratings: list[float] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def _parse_ratings(raw: Any) -> list[float]:
        """Converts ratings to a list of floats, limiting values between 0 and 5 and to 2 decimal places."""
        result = []
        if not (raw is None or raw == ""):
            if isinstance(raw, (list, tuple)):
                sequence = raw
            elif isinstance(raw, (int, float)):
                sequence = [raw]
            elif isinstance(raw, str):
                context = raw.strip()
                if context.startswith("[") and context.endswith("]"):
                    try:
                        sequence = json.loads(context)
                    except Exception:
                        return []
                else:
                    sequence = [p for p in re.split(r"[,\|\;\s]+", context) if p]

            for value in sequence:
                try:
                    val = float(value)
                    val = min(5.0, max(0.0, val))
                    val = round(val, 2)
                    result.append(val)
                except (TypeError, ValueError):
                    continue
        return result

    @classmethod
    def from_row(cls, row: dict[str, Any], source: str) -> "ImportData":
        """Method to create an ImportData instance from a data row.
        Args:
            row (dict[str, Any]): The data row to convert.
            source (str): The source type of the data.
        Raises:
            ValueError: If the data is invalid or the source is unknown.
        Returns:
            ImportData: The created ImportData instance.
        """
        match source:
            case SourceType.CSV:
                ratings = cls._parse_ratings(raw=row.get("poi_ratings"))
                instance = cls(
                    external_id=str(row["poi_id"]).strip(),
                    name=str(row["poi_name"]).strip(),
                    latitude=float(row["poi_latitude"]),
                    longitude=float(row["poi_longitude"]),
                    category=str(row["poi_category"]).strip(),
                    ratings=ratings,
                    description=str(row.get("poi_description") or "").strip(),
                )
                return instance
            case SourceType.JSON:
                ratings = cls._parse_ratings(raw=row.get("ratings"))
                coords = row.get("coordinates")
                lat, lon = None, None
                if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    try:
                        lat = float(coords[0])
                        lon = float(coords[1])
                    except (TypeError, ValueError):
                        lat, lon = None, None
                elif isinstance(coords, dict):
                    try:
                        lat_raw = coords.get("latitude")
                        lon_raw = coords.get("longitude")
                        lat = float(lat_raw) if lat_raw is not None else None
                        lon = float(lon_raw) if lon_raw is not None else None
                    except (TypeError, ValueError):
                        lat, lon = None, None
                if lat is None or lon is None:
                    raise ValueError("Invalid or missing coordinates in JSON row")
                instance = cls(
                    external_id=str(row["id"]).strip(),
                    name=str(row["name"]).strip(),
                    latitude=lat,
                    longitude=lon,
                    category=str(row["category"]).strip(),
                    ratings=ratings,
                    description=str(row.get("description") or "").strip(),
                )
                return instance
            case SourceType.XML:
                ratings = cls._parse_ratings(raw=row.get("pratings"))
                instance = cls(
                    external_id=str(row["pid"]).strip(),
                    name=str(row["pname"]).strip(),
                    latitude=float(row["platitude"]),
                    longitude=float(row["plongitude"]),
                    category=str(row["pcategory"]).strip(),
                    ratings=ratings,
                    description=str(row.get("pdescription") or "").strip(),
                )
                return instance
            case _:
                raise ValueError(f"Unknown source: {source}")
