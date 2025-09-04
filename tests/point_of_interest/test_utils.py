import uuid

import pytest

import point_of_interest.utils as utils
from point_of_interest.enums import SourceType
from point_of_interest.utils import (
    batched,
    iter_xml_dicts,
    normalize_record,
    source_from_path,
    validate_uuid,
)
from tests.point_of_interest.conftest import DummyImportData, FailingImportData


@pytest.mark.parametrize(
    "uuid_str, expected",
    [
        (str(uuid.uuid4()), True),
        ("test", False),
        ("", False),
    ],
)
def test_validate_uuid(uuid_str, expected):
    """Test that validate_uuid correctly identifies valid and invalid UUIDv4 strings."""
    assert validate_uuid(uuid_str) == expected


@pytest.mark.parametrize(
    "fname, expected",
    [
        ("sample.csv", SourceType.CSV),
        ("data.JSON", SourceType.JSON),
        ("items.xml", SourceType.XML),
    ],
)
def test_source_from_path_supported_extensions(tmp_path, fname, expected):
    """Test that source_from_path correctly infers source type from supported extensions."""
    p = tmp_path / fname
    p.write_text("", encoding="utf-8")
    assert source_from_path(p) == expected


def test_source_from_path_unsupported_extension(tmp_path):
    """Test that source_from_path raises ValueError for unsupported extensions."""
    p = tmp_path / "notes.txt"
    p.write_text("", encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        source_from_path(p)
    assert "Unsupported file extension" in str(exc.value)


def test_normalize_record_success(monkeypatch):
    """Test that normalize_record successfully uses ImportData.from_row and to_dict."""
    monkeypatch.setattr(utils, "ImportData", DummyImportData, raising=True)

    row = {"any": "data"}
    out = normalize_record(row, SourceType.CSV)
    assert out == {"ok": True, "row": row, "source": SourceType.CSV}


def test_normalize_record_failure_bubbles_as_valueerror(monkeypatch):
    """Test that errors in ImportData.from_row are caught and re-raised as ValueError."""
    monkeypatch.setattr(utils, "ImportData", FailingImportData, raising=True)

    with pytest.raises(ValueError) as exc:
        normalize_record({"x": 1}, SourceType.JSON)
    assert "Error normalizing record: boom" in str(exc.value)


def test_iter_xml_dicts_yields_required_nodes(tmp_path):
    """Test that iter_xml_dicts correctly yields dictionaries for each <poi> element."""
    xmlp = tmp_path / "pois.xml"
    xmlp.write_text(
        """<pois>
            <poi>
                <pid>E1</pid>
                <pname> Cafe </pname>
                <platitude>1.1</platitude>
                <plongitude>2.2</plongitude>
                <pcategory>cafe</pcategory>
                <pratings>4|5</pratings>
            </poi>
            <poi>
                <pid>E2</pid>
                <pname>Park</pname>
                <platitude>3.3</platitude>
                <plongitude>4.4</plongitude>
                <pcategory>park</pcategory>
                <pratings>[3,4]</pratings>
            </poi>
        </pois>""",
        encoding="utf-8",
    )
    items = list(iter_xml_dicts(xmlp))
    assert len(items) == 2
    assert items[0]["pid"] == "E1"
    assert items[0]["pname"] == "Cafe"
    assert set(items[0].keys()) == {
        "pid",
        "pname",
        "platitude",
        "plongitude",
        "pcategory",
        "pratings",
    }


@pytest.mark.parametrize(
    "data, size, expected",
    [
        (list(range(0, 5)), 2, [[0, 1], [2, 3], [4]]),
        ([], 3, []),
        ([1, 2, 3], 10, [[1, 2, 3]]),
    ],
)
def test_batched(data, size, expected):
    """Test that batched yields correct slices of the input sequence."""
    assert [list(chunk) for chunk in batched(data, size)] == expected
