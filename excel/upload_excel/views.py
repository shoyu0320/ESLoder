from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

import openpyxl
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from upload_excel.forms import ColumnForm, ContentForm, RowForm, UploadForm
from upload_excel.models import ExcelSheetModel

_QS = TypeVar("_QS", bound=QuerySet)

class UploadExcelView(TemplateView):
    form_class = UploadForm
    template_name = "upload_excel/index.html"
    uploaded_template = "upload_excel/upload.html"
    success_url = reverse_lazy("excel:upload")

    def _get_basic_context(self) -> dict[str, Any]:
        return {
            "user_id": "3f5017be-a314-4bb2-92c0-5135b47f8c45"
        }

    def _make_display_context(self,
                              excel_sheet_model: ExcelSheetModel) -> List[str]:
        cell_ranges: _QS = excel_sheet_model.cell_ranges.all()
        output: dict[int, List[dict[str, str]]] = {}
        _out: dict[str, str]
        for merged_cell in cell_ranges:
            _out = {}

            column = merged_cell.columns.filter(cell_range=merged_cell).all().last()
            _out["col_start"] = column.cell_start
            _out["col_end"] = column.cell_end
            _out["col_size"] = column.cell_size

            row = merged_cell.rows.filter(cell_range=merged_cell).all().last()
            _out["row_start"] = row.cell_start
            _out["row_end"] = row.cell_end
            _out["row_size"] = row.cell_size

            content = merged_cell.content.filter(cell_range=merged_cell).all().last()
            _out["content"] = content.cell_content

            coord = int(_out["row_start"])
            if coord not in output:
                for c in range(1, coord + 1):
                    if c not in output:
                        output[c] = []
            output[coord] += [_out]
        return output

    def post(self, request: HttpRequest, *args, **kwargs):
        context: dict[str, Any] = self._get_basic_context()
        if request.method == "POST":
            # openpyxl はバイナリファイルを指定してあげることもできる。許せない。
            # 参考: https://stackoverflow.com/questions/20635778/using-openpyxl-to-read-file-from-memory
            esm: ExcelSheetModel = ExcelSheetModel.create_model(request, file_key="file", sheet_type="profile")
            context["display"] = {}
            context["display"] = self._make_display_context(esm)

        return render(request, self.template_name, context=context)

    def get(self, request: HttpRequest,
            *args: Tuple[Any, ...],
            **kwargs: dict[str, Any]) -> HttpResponse:
        context: dict[str, Any] = self._get_basic_context()
        context["upload"] = self.form_class()
        context["display"] = None
        return render(request, self.template_name, context=context)


class DisplaySheetView(TemplateView):
    form_class = UploadForm
    template_name = "upload_excel/upload.html"
    success_url = reverse_lazy("index")

    def _get_basic_context(self) -> dict[str, Any]:
        return {
            "user_id": "3f5017be-a314-4bb2-92c0-5135b47f8c45"
        }

    def get(self, request: HttpRequest,
            *args: Tuple[Any, ...],
            **kwargs: dict[str, Any]) -> HttpResponse:
        context: dict[str, Any] = self._get_basic_context()
        return render(request, self.template_name, context=context)
