"""
Authentication generalized definitions.
"""
from importlib import import_module

from django.conf import settings


def get_bearer_authentication_allow_inactive_user_class():
    """
    Wrapper for `lms.djangoapps.courseware.courses.has_access`
    """
    backend_function = settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_AUTHENTICATION_BACKEND
    backend = import_module(backend_function)

    return backend.BearerAuthenticationAllowInactiveUser


BearerAuthenticationAllowInactiveUser = (
    get_bearer_authentication_allow_inactive_user_class()
)
