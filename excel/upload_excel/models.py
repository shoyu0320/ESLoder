import re
import uuid
from typing import Any, Callable, List, Optional, Tuple, TypeVar

import openpyxl
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.utils import ProgrammingError
from django.http import HttpRequest
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.cell_range import CellRange
from openpyxl.worksheet.worksheet import Worksheet

_T = TypeVar("_T", bound=models.Model)
_F = TypeVar("_F", bound=models.Field)
_CRM = TypeVar("_CRM", bound="CellRangeModel")
_ESM = TypeVar("_ESM", bound="ExcelSheetModel")
_EST = TypeVar("_EST", bound="ESTemplateNamesModel")
_CM = TypeVar("_CM", bound="ColumnModel")
_RM = TypeVar("_RM", bound="RowModel")
_CTM = TypeVar("_CTM", bound="ContentModel")

# 改行パターン
br_pattern: str = "?#$%&@!?*+"


getters = {
    "digit": re.compile(r"\d+").findall,
    "alphabet": re.compile(r"([A-Z]+)").findall
}


def get_bound_items(cell_range: CellRange,
                    bound_type: str = "digit") -> Tuple[str, str]:
    # preparations
    if bound_type not in getters:
        raise KeyError("'bound_type' must be either ''digit' or 'alphabet'")

    getter: str = getters[bound_type]
    str_coord: str = cell_range.coord

    # set
    start: str
    end: str
    start, end = str_coord.split(":")
    start = getter(start)[0]
    end = getter(end)[0]

    return start, end


def get_cell_value(cell: Cell, concat_size: int = 0) -> Optional[str]:
    val: Optional[Any] = cell.value
    output: str = ""
    if val is not None:
        if concat_size > 0:
            output += br_pattern
        output += str(val)
    return output


class ESTemplateNamesModel(models.Model):
    name: _F = models.CharField(
        verbose_name="シートタイプ",
        blank=False,
        null=False,
        default="profile",
        editable=True,
        max_length=20,
    )
    init_choices: List[str] = [
        (1, "profile"), (2, "project")
    ]
    class Meta:
        db_table: str = "template_names"

    @classmethod
    def add(cls, val: str) -> None:
        template_name_model: _EST = cls(name=val)
        template_name_model.save(force_insert=True)

    @classmethod
    def _get_template_names(cls, *args, **kwargs) -> List[str]:
        output: List[str] = [] + cls.init_choices
        count: int = 3
        _choices: List[str] = [c for _, c in cls.init_choices]
        # exception process when using makemigration command as initialization.
        try:
            for v in ESTemplateNamesModel.objects.all().values_list():
                if v in _choices:
                    continue
                output += [(count, v)]
                count += 1
                _choices += [v]
            return output
        except ProgrammingError:
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
        primary_key=True,
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
        choices=ESTemplateNamesModel._get_template_names()
    )
    class Meta:
        db_table: str = "excel_sheet"

    @classmethod
    def is_valid_request(self,
                         request: HttpRequest,
                         file_key: str = "file"
                         ) -> None:
        is_valid: bool = file_key in request.FILES
        if not is_valid:
            raise KeyError()

    @classmethod
    def get_binary_data(cls,
                        request: HttpRequest,
                        file_key: str = "file") -> str:
        file_data: List[InMemoryUploadedFile] = request.FILES[file_key]
        return file_data.file

    @classmethod
    def create_model(cls,
                     request: HttpRequest,
                     file_key: str = "file",
                     sheet_type: str = "profile") -> _ESM:
        cls.is_valid_request(request, file_key)
        binary: str = cls.get_binary_data(request, file_key)

        workbook: Workbook = openpyxl.load_workbook(binary)
        excel_sheet_model: _ESM = cls(sheet_type=sheet_type)
        excel_sheet_model.save(force_insert=True)

        excel_sheet_model.create_cell_ranges(workbook)

        return excel_sheet_model

    def create_cell_ranges(self, workbook: Workbook) -> None:

        worksheet: Worksheet = workbook.active

        cell_ranges: List[CellRange] = worksheet.merged_cells.ranges
        ranges: CellRange
        idx: int

        for idx, ranges in enumerate(cell_ranges):
            CellRangeModel.\
                create_model(self, worksheet=worksheet, cell_range=ranges, idx=idx)

# TODO cell range　をA1タイプにして行列それぞれに入力する術を考えること
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
                     worksheet: Worksheet,
                     cell_range: CellRange,
                     idx: int = 0) -> _CRM:

        # When creating a child model,
        # an inputting parent model which has been defined
        # as foreign key model at child must be saved before.
        crm: _CRM = cls(excel_sheet=excel_sheet,
                        cell_range_id_by_order=idx)
        crm.save(force_insert=True)
        ColumnModel.create_model(cell_range_model=crm,
                                 cell_range=cell_range,
                                 idx=idx)
        RowModel.create_model(cell_range_model=crm,
                              cell_range=cell_range,
                              idx=idx)
        ContentModel.create_model(cell_range_model=crm,
                                  worksheet=worksheet,
                                  cell_range=cell_range,
                                  idx=idx)
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
    cell_size: _F = models.PositiveIntegerField(
        verbose_name="セルの列方向サイズ",
        blank=False,
        null=False,
        default=1,
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
        db_table: str = "column"

    @classmethod
    def create_model(cls,
                     cell_range_model: _CRM,
                     cell_range: CellRange,
                     idx: int = 0) -> _CM:
        start, end = get_bound_items(cell_range, bound_type="alphabet")
        cell_size: int = cell_range.max_col - cell_range.min_col + 1
        column: _CM = cls(cell_range=cell_range_model,
                         cell_start=start,
                         cell_end=end,
                         cell_size=cell_size,
                         cell_range_id_by_order=idx)
        column.save(force_insert=True)
        return column


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
    cell_size: _F = models.PositiveIntegerField(
        verbose_name="セルの行方向サイズ",
        blank=False,
        null=False,
        default=1,
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
        db_table: str = "row"

    @classmethod
    def create_model(cls,
                     cell_range_model: _CRM,
                     cell_range: CellRange,
                     idx: int = 0) -> _RM:
        start, end = get_bound_items(cell_range, bound_type="digit")
        cell_size: int = cell_range.max_row - cell_range.min_row + 1
        row: _RM = cls(cell_range=cell_range_model,
                       cell_start=start,
                       cell_end=end,
                       cell_size=cell_size,
                       cell_range_id_by_order=idx)
        row.save(force_insert=True)
        return row



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

    @classmethod
    def extract_cell_content(cls,
                             worksheet: Worksheet,
                             cell_range: CellRange) -> str:
        coord: str = cell_range.coord
        start, end = coord.split(":")
        cell_info: Tuple[Tuple[Cell, ...]] = worksheet[start:end]
        output: str = ""
        for cell_row in cell_info:
            for cell in cell_row:
                concat_size = len(output)
                output += get_cell_value(cell, concat_size)
        return output

    @classmethod
    def create_model(cls,
                     cell_range_model: _CRM,
                     worksheet: Worksheet,
                     cell_range: CellRange,
                     idx: int = 0) -> _CTM:
        cell_content = cls.extract_cell_content(worksheet, cell_range)
        content: _CTM = cls(cell_range=cell_range_model,
                            cell_content=cell_content,
                            cell_range_id_by_order=idx)
        content.save(force_insert=True)
        return content
