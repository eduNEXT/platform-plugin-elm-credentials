"""
Production settings for the plugin.
"""


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_AUTHENTICATION_BACKEND = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "PLATFORM_PLUGIN_ELM_CREDENTIALS_AUTHENTICATION_BACKEND",
        settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_AUTHENTICATION_BACKEND,
    )
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_COURSE_OVERVIEWS_BACKEND = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "PLATFORM_PLUGIN_ELM_CREDENTIALS_COURSE_OVERVIEWS_BACKEND",
        settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_COURSE_OVERVIEWS_BACKEND,
    )
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND",
        settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND,
    )
