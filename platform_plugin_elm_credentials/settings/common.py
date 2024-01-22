"""
Common settings for the plugin.
"""


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_AUTHENTICATION_BACKEND = (
        "platform_plugin_elm_credentials.edxapp_wrapper.backends.authentication_p_v1"
    )
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_MODULESTORE_BACKEND = (
        "platform_plugin_elm_credentials.edxapp_wrapper.backends.modulestore_p_v1"
    )
    settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND = (
        "platform_plugin_elm_credentials.edxapp_wrapper.backends.certificates_p_v1"
    )
