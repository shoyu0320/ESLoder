from typing import Tuple

from django import forms

from excel.upload_excel.models import ColumnModel, ContentModel, RowModel


class UploadForm(forms.Form):
    file = forms.FileField()


class ColumnForm(forms.ModelForm):
    class Meta:
        model: ColumnModel = ColumnModel
        fields: Tuple[str, ...] = (
            "cell_start", "cell_end"
        )


class RowForm(forms.ModelForm):
    class Meta:
        model: RowModel = RowModel
        fields: Tuple[str, ...] = (
            "cell_start", "cell_end"
        )


class ContentForm(forms.ModelForm):
    class Meta:
        model: ContentModel = ContentModel
        fields: Tuple[str, ...] = (
            "cell_content",
        )