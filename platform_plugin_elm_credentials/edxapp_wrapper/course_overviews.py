"""
Wrapper methods of course_overviews in edx-platform.
"""
from importlib import import_module

from django.conf import settings


def get_course_overview_or_none(*args, **kwargs):
    """
    Wrapper method of get_course_overview_or_none in edx-platform.
    """
    backend_function = settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_COURSE_OVERVIEWS_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_overview_or_none(*args, **kwargs)
