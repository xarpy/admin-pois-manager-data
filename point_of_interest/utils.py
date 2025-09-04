import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterator, Sequence
from uuid import UUID

from point_of_interest.enums import SourceType
from point_of_interest.schemas import ImportData


def validate_uuid(uuid_string: str) -> bool:
    """Function responsible to check the uuid input
    Args:
        uuid_string (str): Receives the input string
    Returns:
        bool: Return a boolean with the validation result
    """
    result = True
    try:
        UUID(uuid_string, version=4)
    except ValueError:
        result = False
    return result


def source_from_path(path: Path) -> str | ValueError:
    """Infer source type from file suffix.
    Args:
        path (Path): Receives the file path to infer the source type from.
    Raises:
        ValueError: If the file extension is unsupported.
    Returns:
        str: Return the inferred source type or a ValueError if unsupported.
    """
    extension = path.suffix.lower()
    match extension:
        case ".csv":
            return SourceType.CSV
        case ".json":
            return SourceType.JSON
        case ".xml":
            return SourceType.XML
        case _:
            raise ValueError(f"Unsupported file extension: {extension}")


def normalize_record(row: dict[str, Any], source: str) -> dict[str, Any]:
    """
    Normalize a data row based on its source type.
    Args:
        row (dict[str, Any]): Input record.
        source (str): Source type of the data.
    Raises:
        ValueError: If the source type is unknown.
    Returns:
        dict[str, Any]: Normalized record as a dictionary.
    """
    try:
        result = ImportData.from_row(row, source)
        return result.to_dict()
    except Exception as exc:
        raise ValueError(f"Error normalizing record: {exc}") from exc


def iter_xml_dicts(path: Path) -> Iterator[dict[str, Any]]:
    """Function to iterate over XML file and yield dicts for each PoI-like node.
    Args:
        path (Path): Path to the XML file.
    Yields:
        Iterator[dict[str, Any]]: Dict representation of each PoI-like node.
    """
    required = {"pid", "pname", "platitude", "plongitude", "pcategory", "pratings"}
    tree = ET.parse(path)
    root = tree.getroot()
    for node in root.iter():
        tags = {c.tag for c in node}
        if required.issubset(tags):
            yield {child.tag: (child.text or "").strip() for child in node}


def batched(seq: Sequence[Any], batch_size: int) -> Iterator[Sequence[Any]]:
    """Function to yield slices (batches) of seq with size batch_size.
    Args:
        seq (Sequence[Any]): The input sequence to batch.
        batch_size (int): The size of each batch.
    Yields:
        Iterator[Sequence[Any]]: Batches of the input sequence.
    """
    for i in range(0, len(seq), batch_size):
        yield seq[i : i + batch_size]
