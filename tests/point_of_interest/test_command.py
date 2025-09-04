import pytest
from django.core.management import call_command

from point_of_interest.models import POI


@pytest.mark.django_db
def test_import_poi_file_success(tmp_path, capsys):
    """Test that the import_poi_file command runs successfully and creates POI records."""
    csv_path = tmp_path / "pois.csv"
    csv_path.write_text(
        "poi_id,poi_name,poi_latitude,poi_longitude,poi_category,poi_ratings\n"
        'E1,Park,1.1,2.2,park,"4,5"\n'
    )
    call_command(
        "import_poi_file", str(csv_path), "--chunksize", "5", "--batch-size", "5"
    )
    captured = capsys.readouterr()
    assert "Data processed successfully" in captured.out
    assert "created: 1" in captured.out
    assert "updated: 0" in captured.out
    assert POI.objects.filter(external_id="E1").exists()


@pytest.mark.django_db
def test_import_poi_file_missing_file(tmp_path, capsys):
    """Test that the command handles a missing file gracefully."""
    missing = tmp_path / "nope.csv"
    call_command("import_poi_file", str(missing))
    captured = capsys.readouterr()
    assert "Failed processing" in captured.err or "Unexpected error" in captured.err
