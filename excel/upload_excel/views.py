import string
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from upload_excel.forms import ColumnForm, ContentForm, RowForm, UploadForm
from upload_excel.models import (CellRangeModel, ColumnModel, ContentModel,
                                 ExcelSheetModel, RowModel)
from upload_excel.utils.sort import A2ZListMaker

_QS = TypeVar("_QS", bound=QuerySet)
_CONTENT = TypeVar("_CONTENT", bound=Union[ColumnModel, ContentModel, RowModel])


class UploadExcelView(TemplateView):
    form_class = UploadForm
    template_name = "upload_excel/index.html"
    uploaded_template = "upload_excel/index.html"
    success_url = reverse_lazy("upload_excel:upload")
    url_tmp: str = "upload_excel:upload"

    def _get_basic_context(self) -> dict[str, Any]:
        return {
            "user_id": self.kwargs.get("user_id", "null")
        }

    def get_excel_col_size(self, excel_sheet_model: ExcelSheetModel) -> List[str]:
        excel_col_order_maker: A2ZListMaker =\
            A2ZListMaker(max_size=excel_sheet_model.col_size, init=string.ascii_uppercase)
        excel_col_order_maker.create()
        return excel_col_order_maker.values

    def _calc_total_size(self,
                             cells: List[dict[str, _CONTENT]],
                             key: str = "columns") -> int:
        output: int = 0
        for cell in cells:
            output += cell[key].cell_size
        return output

    def get_col_last_label(self,
                           excel_dict: dict[int, List[dict[str, _CONTENT]]],
                           col_list: List[str]) -> str:
        temp: List[int] = []
        last_label: str
        for cells in excel_dict.values():
            last_label = cells["column"].cell_end
            temp += [col_list.index(last_label)]
        last_idx: int = max(temp)
        return col_list[last_idx]

    def _calc_col_max_size(self, excel_dict: dict[int, List[dict[str, _CONTENT]]]) -> int:
        temp: List[int] = []
        for cells in excel_dict.values():
            temp += [self._calc_total_size(cells, "column")]
        return max(temp)

    def sort_dict_by(self,
                     excel_dict: dict[int, List[dict[str, _CONTENT]]],
                     key: List[str],
                     col_order: List[str],
                     ) -> dict[int, List[dict[str, _CONTENT]]]:
        output: dict[int, List[dict[str, _CONTENT]]] = {}
        for i, cells in excel_dict.items():
            if len(cells) == 0:
                continue
            output[i] = sorted(cells, key=lambda x: key.index(x["column"].cell_start))
        return output

    # [x] TODO セル幅を最小のサイズにまで落とす
    # 全てのセルサイズを 1 に初期化 → 隣接(横か縦かを記憶)項目分だけリサイズ
    # tree作る -> セル同士の隣接グラフを作成（50%超過の包含の場合を隣接とする; 隣接頂点は無向グラフ; あるいは上から下、左から右の有向グラフ）
    # -> 下/右に分けて、それぞれ横/縦のサイズを決定する; 基本的には上側/左側の方が大きいことを利用する
    # なぜやるか; html表示にする際に表として表示したかったのだが、最小サイズ以外だと下に欲しい項目が横に来ることがあったため。しね。
    def _make_display_context(self,
                              excel_sheet_model: ExcelSheetModel) -> List[str]:
        excel_col_order: List[str] = self.get_excel_col_size(excel_sheet_model)
        cell_ranges: _QS = excel_sheet_model.cell_ranges.all()
        output: dict[int, List[dict[str, _CONTENT]]] = {}
        _out: dict[str, _CONTENT]
        for merged_cell in cell_ranges:
            _out = {"merged_cell": merged_cell}

            column = merged_cell.columns.filter(cell_range=merged_cell).all().last()
            _out["column"] = column

            row = merged_cell.rows.filter(cell_range=merged_cell).all().last()
            _out["row"] = row

            content = merged_cell.content.filter(cell_range=merged_cell).all().last()
            _out["content"] = content

            coord = int(_out["row"].cell_start)
            if coord not in output:
                for c in range(1, coord + 1):
                    if c not in output:
                        output[c] = []
            output[coord] += [_out]

        return self.sort_dict_by(output, key=excel_col_order, col_order=excel_col_order)

    def post(self, request: HttpRequest, *args, **kwargs):
        context: dict[str, Any] = self._get_basic_context()
        if request.method == "POST":
            # openpyxl はバイナリファイルを指定してあげることもできる。許せない。
            # 参考: https://stackoverflow.com/questions/20635778/using-openpyxl-to-read-file-from-memory
            esm: ExcelSheetModel = ExcelSheetModel.create_model(request, file_key="file", sheet_type="profile")
            context["display"] = self._make_display_context(esm)
            context["excel_id"] = esm.sheet_id
            url = reverse_lazy(self.url_tmp, kwargs={"user_id": esm.sheet_id})
            return redirect(url)

        return render(request, self.template_name, context=context)

    def get(self, request: HttpRequest,
            *args: Tuple[Any, ...],
            **kwargs: dict[str, Any]) -> HttpResponse:
        context: dict[str, Any] = self._get_basic_context()
        context["upload"] = self.form_class()
        context["display"] = None
        context["excel_id"] = self.kwargs.get("excel_id", "before_upload")
        print(self.kwargs)
        return render(request, self.template_name, context=context)



class CellUploadView(UploadExcelView):
    template_name:str = "upload_excel/upload.html"
    success_url: str = reverse_lazy("upload_excel:upload")

    def get(self, request: HttpRequest,
            *args: Tuple[Any, ...],
            **kwargs: dict[str, Any]) -> HttpResponse:
        context: dict[str, Any] = self._get_basic_context()
        user_id: str = self.kwargs["user_id"]
        esm: ExcelSheetModel = ExcelSheetModel.objects.get(sheet_id=user_id)
        context["excel_id"] = esm.sheet_id
        context["display"] = self._make_display_context(esm)
        return render(request, self.template_name, context=context)

class CellUpdateView(UploadExcelView):
    form_class = ContentForm
    template_name: str = "upload_excel/update.html"
    success_url: str = reverse_lazy("upload_excel:upload")

    def _get_basic_context(self) -> dict[str, Any]:
        return {
            "user_id": self.kwargs["user_id"],
            "cell_id": self.kwargs["cell_id"],
            "cell_uuid": self.kwargs["cell_uuid"],
        }

    def get_success_url(self) -> str:
        kwargs: dict[str, Any] = self._get_attrs()
        url: str = self._get_url(kwargs)
        return reverse_lazy(url, kwargs=kwargs)

    def get_cell_range_from_db(self, cell_id: int, cell_uuid: str) -> Tuple[str, str]:
        cell_range: CellRangeModel = CellRangeModel.objects.\
            get(cell_range_id_by_order=cell_id, cell_range_id=cell_uuid)
        row_data: RowModel = RowModel.objects.get(cell_range=cell_range)
        col_data: ColumnModel = ColumnModel.objects.get(cell_range=cell_range)

        start: str = col_data.cell_start + row_data.cell_start
        end: str = col_data.cell_end + row_data.cell_end
        return (start, end)

    def get_cell_text_from_db(self, cell_id: int, cell_uuid: str) -> str:
        cell_range: CellRangeModel = CellRangeModel.objects.\
            get(cell_range_id_by_order=cell_id, cell_range_id=cell_uuid)
        content: ContentModel = ContentModel.objects.get(cell_range=cell_range)

        return content.cell_content

    def post(self, request: HttpRequest, *args, **kwargs):
        context: dict[str, Any] = self._get_basic_context()
        if request.method == "POST":
            user_id: str = self.kwargs["user_id"]
            cell_id: str = self.kwargs["cell_id"]
            cell_uuid: str = self.kwargs["cell_uuid"]
            cell_range: CellRangeModel = CellRangeModel.objects.\
                get(cell_range_id_by_order=cell_id, cell_range_id=cell_uuid)
            content: ContentModel = ContentModel.objects.get(cell_range=cell_range)
            form = self.form_class(request.POST, initial_text=content.cell_content, instance=content)
            if form.is_valid():
                form.save()

            esm: ExcelSheetModel = ExcelSheetModel.objects.get(sheet_id=user_id)
            context["excel_id"] = esm.sheet_id
            context["display"] = self._make_display_context(esm)

        return render(request, "upload_excel/upload.html", context=context)

    def get(self, request: HttpRequest,
            *args: Tuple[Any, ...],
            **kwargs: dict[str, Any]) -> HttpResponse:
        context: dict[str, Any] = self._get_basic_context()
        args: Tuple[str, str] = context["cell_id"], context["cell_uuid"]
        context["cell"] = self.get_cell_range_from_db(*args)
        context["content"] = self.form_class(initial_text=self.get_cell_text_from_db(*args))
        return render(request, self.template_name, context)

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
