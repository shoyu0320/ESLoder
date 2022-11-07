from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

import openpyxl
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from excel.upload_excel.forms import (ColumnForm, ContentForm, RowForm,
                                      UploadForm)
from excel.upload_excel.models import ExcelSheetModel

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
        output: List[str] = []
        for merged_cell in cell_ranges:
            cols_start = cell_ranges.columns.cell_start
            cols_end = cell_ranges.columns.cell_end
            rows_start = cell_ranges.rows.cell_start
            rows_end = cell_ranges.rows.cell_end
            content = cell_ranges.content.cell_content
            output += [content]
        return output

    def post(self, request, *args, **kwargs):
        context: dict[str, Any] = self._get_basic_context()
        if request.method == "POST":
            # openpyxl はバイナリファイルを指定してあげることもできる。許せない。
            # 参考: https://stackoverflow.com/questions/20635778/using-openpyxl-to-read-file-from-memory
            esm: ExcelSheetModel = ExcelSheetModel.create_model(request, file_key="file", sheet_type="profile")
            esm.save(force_insert=True)
            context["display"] = {}
            context["display"] = self._make_display_context(esm)

        return render(request, self.uploaded_template, context=context)

    def get(self, request: HttpRequest,
            *args: Tuple[Any, ...],
            **kwargs: dict[str, Any]) -> HttpResponse:
        context: dict[str, Any] = self._get_basic_context()
        context["upload_form"] = self.form_class()
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
