"""URL patterns for the platform_plugin_elm_credentials plugin."""
from django.urls import path

from platform_plugin_elm_credentials.api import views

app_name = "platform_plugin_elm_credentials"

urlpatterns = [
    path(
        "credential-builder/",
        views.ElmCredentialBuilderAPIView.as_view(),
        name="credential-builder-api",
    ),
]
