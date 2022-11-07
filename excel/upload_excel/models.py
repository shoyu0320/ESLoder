import uuid
from typing import Any, List, TypeVar

import openpyxl
from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.worksheet.cell_range import CellRange
from openpyxl.worksheet.worksheet import Worksheet

_T = TypeVar("_T", bound=models.Model)
_F = TypeVar("_F", bound=models.Field)
_CRM = TypeVar("_CRM", bound="CellRangeModel")
_ESM = TypeVar("_ESM", bound="ExcelSheetModel")
_EST = TypeVar("_EST", bound="ESTemplateNamesModel")


class ESTemplateNamesModel(models.Model):
    name: _F = models.CharField(
        verbose_name="シートタイプ",
        blank=False,
        null=False,
        default="profile",
        editable=True,
        max_length=20,
    )
    init_choices: List[str] = ["profile", "project"]
    class Meta:
        db_table: str = "template_names"

    @classmethod
    def add(cls, val: str) -> None:
        template_name_model: _EST = cls(name=val)
        template_name_model.save(force_insert=True)

    @classmethod
    def get_template_names(cls, *args, **kwargs) -> List[str]:
        output: List[str] = [] + cls.init_choices
        output += list(cls.objects.values_list("name"))
        return output

class ExcelSheetModel(models.Model):
    sheet_create_time: _F = models.DateTimeField(
        verbose_name="シート作成日時",
        blank=False,
        null=False,
        default=timezone.now,
        help_text=(
            "Define when a sheet has created."
        ),
    )
    sheet_update_time: _F = models.DateTimeField(
        verbose_name="シート作成日時",
        blank=False,
        null=False,
        default=timezone.now,
        help_text=(
            "Define when a sheet has updated."
        )
    )
    sheet_id: _F = models.UUIDField(
        verbose_name="シートID",
        blank=False,
        null=False,
        default=uuid.uuid4(),
        editable=True,
        help_text=(
            "An ID based on uuid4 is assigned by sheet randomly and automatically."
        )
    )
    sheet_type: _F = models.CharField(
        verbose_name="シートタイプ",
        blank=False,
        null=False,
        default="profile",
        editable=True,
        max_length=10,
        help_text=(
            "Set a name of template sheet."
            "'profile' that is default sheet type is a template "
            "we designed as typical profile in our office"
            "Even before you don't generate your custom template, "
            "you can use two template types of 'profile' and 'project'"
        ),
        choices=ESTemplateNamesModel.get_template_names
    )
    class Meta:
        db_table: str = "excel_sheet"

    @classmethod
    def create_model(cls,
                     request: HttpRequest,
                     file_key: str = "file",
                     sheet_type: str = "profile") -> _ESM:
        uploaded_xlsx: List[Any] = request.FILES.get(file_key, None)
        if uploaded_xlsx is None:
            raise ValueError()
        else:
            binary: str = getattr(uploaded_xlsx, file_key)

        workbook: Workbook = openpyxl.load_workbook(binary)
        excel_sheet_model: _ESM = cls(sheet_type=sheet_type)

        excel_sheet_model.create_cell_ranges(workbook)

        return excel_sheet_model

    def create_cell_ranges(self, workbook: Workbook) -> None:

        worksheet: Worksheet = workbook.active

        cell_ranges: List[CellRange] = worksheet.merged_cells.ranges
        cell_range_model: _CRM
        ranges: CellRange
        idx: int

        for idx, ranges in enumerate(cell_ranges):
            cell_range_model = CellRangeModel.create_model(self,
                                                           cell_range=ranges,
                                                           idx=idx)
            cell_range_model.save(force_insert=True)

class CellRangeModel(models.Model):
    excel_sheet: _F = models.ForeignKey(
        ExcelSheetModel,
        on_delete=models.CASCADE,
        related_name="cell_ranges"
    )
    sheet_create_time: _F = models.DateTimeField(
        verbose_name="セル範囲作成日時",
        blank=False,
        null=False,
        default=timezone.now,
        help_text=(
            "Define when a sheet has created."
        ),
    )
    sheet_update_time: _F = models.DateTimeField(
        verbose_name="セル範囲作成日時",
        blank=False,
        null=False,
        default=timezone.now,
        help_text=(
            "Define when a sheet has updated."
        )
    )
    cell_range_id: _F = models.UUIDField(
        verbose_name="セル範囲ID",
        blank=False,
        null=False,
        default=uuid.uuid4(),
        editable=True,
        help_text=(
            "An ID based on uuid4 is assigned by cell range randomly and automatically."
        )
    )
    cell_range_id_by_order: _F = models.IntegerField(
        verbose_name="順序付きセル範囲ID",
        blank=False,
        null=False,
        default=None,
        editable=True,
        help_text=(
            "An ID based on merged order is assigned by cell range."
        )
    )
    class Meta:
        db_table: str = "cell_range"

    @classmethod
    def create_model(cls,
                     excel_sheet: _ESM,
                     cell_range: CellRange,
                     idx: int = 0) -> _CRM:

        crm: _CRM = cls(excel_sheet=excel_sheet,
                        cell_range_id_by_order=idx)
        crm.save(force_insert=True)
        cols: List[str] = list(cell_range.cols)
        clm: ColumnModel = ColumnModel(cell_range=crm,
                                      cell_start=cols[0],
                                      cell_end=cols[-1],
                                      cell_range_id_by_order=idx)
        clm.save(force_insert=True)
        rows: List[str] = list(cell_range.rows)
        rwm: RowModel = RowModel(cell_range=crm,
                                cell_start=rows[0],
                                cell_end=rows[-1],
                                cell_range_id_by_order=idx)
        rwm.save(force_insert=True)
        ctm: ContentModel = ContentModel(cell_range=crm,
                                         cell_content="",
                                         cell_range_id_by_order=idx)
        ctm.save(force_insert=True)
        return crm


class ColumnModel(models.Model):
    cell_range: _F = models.ForeignKey(
        CellRangeModel,
        on_delete=models.CASCADE,
        related_name="columns"
    )
    cell_start: _F = models.CharField(
        verbose_name="セルのカラム初期位置",
        blank=False,
        null=False,
        default="A1",
        editable=True,
        max_length=10,
    )
    cell_end: _F = models.CharField(
        verbose_name="セルのカラム終端位置",
        blank=False,
        null=False,
        default="A1",
        editable=True,
        max_length=10,
    )
    cell_range_id_by_order: _F = models.IntegerField(
        verbose_name="順序付きセル範囲ID",
        blank=False,
        null=False,
        default=None,
        editable=True,
        help_text=(
            "An ID based on merged order is assigned by cell range."
        )
    )

    class Meta:
        db_table: str = "column"


class RowModel(models.Model):
    cell_range: _F = models.ForeignKey(
        CellRangeModel,
        on_delete=models.CASCADE,
        related_name="rows"
    )
    cell_start: _F = models.CharField(
        verbose_name="セルのロー初期位置",
        blank=False,
        null=False,
        default="A1",
        editable=True,
        max_length=10,
    )
    cell_end: _F = models.CharField(
        verbose_name="セルのロー終端位置",
        blank=False,
        null=False,
        default="A1",
        editable=True,
        max_length=10,
    )
    cell_range_id_by_order: _F = models.IntegerField(
        verbose_name="順序付きセル範囲ID",
        blank=False,
        null=False,
        default=None,
        editable=True,
        help_text=(
            "An ID based on merged order is assigned by cell range."
        )
    )

    class Meta:
        db_table: str = "row"


class ContentModel(models.Model):
    cell_range: _F = models.ForeignKey(
        CellRangeModel,
        on_delete=models.CASCADE,
        related_name="content"
    )
    cell_content: _F = models.TextField(
        verbose_name="セルの内容",
        blank=False,
        null=False,
        default="",
        editable=True,
    )
    cell_range_id_by_order: _F = models.IntegerField(
        verbose_name="順序付きセル範囲ID",
        blank=False,
        null=False,
        default=None,
        editable=True,
        help_text=(
            "An ID based on merged order is assigned by cell range."
        )
    )
    class Meta:
        db_table: str = "content"
