"""
Enrollments generalized definitions.
"""
from importlib import import_module

from django.conf import settings


def get_user_enrollments(*args, **kwargs):
    """
    Wrapper for `openedx.core.djangoapps.enrollments.data.get_user_enrollments`
    """
    backend_function = settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_ENROLLMENTS_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_enrollments(*args, **kwargs)
