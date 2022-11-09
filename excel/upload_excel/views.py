import string
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from upload_excel.forms import ColumnForm, ContentForm, RowForm, UploadForm
from upload_excel.models import (ColumnModel, ContentModel, ExcelSheetModel,
                                 RowModel)
from upload_excel.utils.sort import A2ZListMaker

_QS = TypeVar("_QS", bound=QuerySet)
_CONTENT = TypeVar("_CONTENT", bound=Union[ColumnModel, ContentModel, RowModel])

class UploadExcelView(TemplateView):
    form_class = UploadForm
    template_name = "upload_excel/index.html"
    uploaded_template = "upload_excel/upload.html"
    success_url = reverse_lazy("excel:upload")

    def _get_basic_context(self) -> dict[str, Any]:
        return {
            "user_id": "3f5017be-a314-4bb2-92c0-5135b47f8c45"
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

            # validation
            if _out["column"].cell_size == 0:
                continue

            if _out["row"].cell_size == 0:
                continue

            if len(_out["content"].cell_content) == 0:
                continue

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
            context["display"] = {}
            context["display"] = self._make_display_context(esm)
            context["excel_id"] = esm.sheet_id

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
