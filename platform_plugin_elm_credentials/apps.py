"""
platform_plugin_elm_credentials Django application initialization.
"""

from django.apps import AppConfig


class PlatformPluginElmCredentialsConfig(AppConfig):
    """
    Configuration for the platform_plugin_elm_credentials Django application.
    """

    name = "platform_plugin_elm_credentials"
    verbose_name = "ELMv3 Credentials Plugin"

    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "platform-plugin-elm-credentials",
                "regex": "platform-plugin-elm-credentials/api/",
                "relative_path": "urls",
            },
        },
        "settings_config": {
            "lms.djangoapp": {
                "test": {"relative_path": "settings.test"},
                "common": {"relative_path": "settings.common"},
                "production": {"relative_path": "settings.production"},
            },
        },
    }
