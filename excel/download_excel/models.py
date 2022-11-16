import uuid
from typing import List, TypeVar

from django.db import models

_F = TypeVar("_F", bound=models.Field)

class DownloadedExcelSheetModel(models.Model):
    downloaded_key: _F = models.UUIDField(
        verbose_name="ダウンロードされたエクセルシートID",
        primary_key=True,
        blank=False,
        null=False,
        default=uuid.uuid4(),
    )
    class Meta:
        db_table: str = "downloaded_excel_sheet"
