from django.urls import path

from . import views, views_utils

app_name = "core"

urlpatterns = [
    path("", views_utils.redirect_to_new_frontend, name="index"),
    path("ready", views.ready, name="ready"),
    path("dashboard/", views_utils.redirect_to_new_frontend, name="dashboard"),
    path("test_logger", views.test_logger, name="test_logger"),
]
