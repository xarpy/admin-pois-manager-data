from django.db import models
from django.utils.translation import gettext_lazy as _


class SourceType(models.TextChoices):
    CSV = "csv", _("CSV")
    JSON = "json", _("JSON")
    XML = "xml", _("XML")
