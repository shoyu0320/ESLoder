from django.urls import path
from download_excel import views

app_name = "download_excel"
urlpatterns = [
    path(
        "user=?<str:user_id>?/download-excel/",
        views.DownloadExcelView.as_view(), name="download"
    ),
]