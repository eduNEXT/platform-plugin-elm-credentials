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
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_MODULESTORE_BACKEND = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "PLATFORM_PLUGIN_ELM_CREDENTIALS_MODULESTORE_BACKEND",
        settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_MODULESTORE_BACKEND,
    )
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND",
        settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND,
    )
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_STUDENT_BACKEND = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "PLATFORM_PLUGIN_ELM_CREDENTIALS_STUDENT_BACKEND",
        settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_STUDENT_BACKEND,
    )
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_ENROLLMENTS_BACKEND = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "PLATFORM_PLUGIN_ELM_CREDENTIALS_ENROLLMENTS_BACKEND",
        settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_ENROLLMENTS_BACKEND,
    )
