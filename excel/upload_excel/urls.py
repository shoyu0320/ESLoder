from django.urls import path

from excel.upload_excel import views

app_name = "SpecSheet"
urlpatterns = [
    path(
        "user=?<str:user_id>?",
        views.ProfileView.as_view(), name="upload"
    ),
]