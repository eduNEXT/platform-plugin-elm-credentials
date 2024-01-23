"""
Certificates generalized definitions.
"""
from importlib import import_module

from django.conf import settings


def get_generated_certificate_model():
    """
    Wrapper for `teams.models.CourseTeam`
    """
    backend_function = settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_CERTIFICATES_BACKEND
    backend = import_module(backend_function)

    return backend.GeneratedCertificate


GeneratedCertificate = get_generated_certificate_model()
