from django.urls import path
from upload_excel import views

app_name = "upload_excel"
urlpatterns = [
    path(
        "user=?<str:user_id>?",
        views.UploadExcelView.as_view(), name="upload"
    ),
]