
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from upload_excel.models import ExcelSheetModel

# Create your views here.

class DownloadExcelView(TemplateView):
    template_name: str = "download_excel/download.html"

    def get(self, request: HttpRequest,
            *args: Tuple[Any, ...],
            **kwargs: dict[str, Any]) -> HttpResponse:
        context: dict[str, Any] = {}
        excel_id: str = self.kwargs.get("user_id", None)
        if excel_id is not None:
            esm: ExcelSheetModel = ExcelSheetModel.objects.get(sheet_id=excel_id)
        return render(request, self.template_name, context=context)