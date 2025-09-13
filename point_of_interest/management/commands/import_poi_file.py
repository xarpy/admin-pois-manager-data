import glob
from typing import Sequence

from django.core.management.base import BaseCommand

from point_of_interest.services import ImportBuilder, ImportServiceError


class Command(BaseCommand):
    help = "Import PoI files (CSV/JSON/XML) with Pandas/ET + upsert in batches."

    def add_arguments(self, parser):
        parser.add_argument(
            "paths", nargs="+", help="Paths to the files (multiple allowed)."
        )
        parser.add_argument(
            "--chunksize",
            type=int,
            default=100_000,
            help="Chunk size for CSV/JSON.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10_000,
            help="Batch size for bulk ops.",
        )

    def handle(self, *args, **opts):

        paths: Sequence[str] = opts["paths"]
        chunksize: int = opts["chunksize"]
        batch_size: int = opts["batch_size"]

        expanded_paths = []
        for p in paths:
            expanded = glob.glob(p)
            if expanded:
                expanded_paths.extend(expanded)
            else:
                expanded_paths.append(p)

        try:
            stats = ImportBuilder(
                expanded_paths, chunksize=chunksize, batch_size=batch_size
            ).run()
            self.stdout.write(self.style.SUCCESS("Data processed successfully"))
            self.stdout.write(
                self.style.WARNING(
                    f"Files processed: {stats.files_processed} | "
                    f"created: {stats.created} | updated: {stats.updated}"
                )
            )
        except ImportServiceError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(self.style.ERROR(f"Unexpected error: {exc}"))
