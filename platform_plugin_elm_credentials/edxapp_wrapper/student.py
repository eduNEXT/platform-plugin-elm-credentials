"""
Student generalized definitions.
"""
from importlib import import_module

from django.conf import settings


def get_user_by_username_or_email(*args, **kwargs):
    """
    Wrapper for `student.models.user.get_user_by_username_or_email`
    """
    backend_function = settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_STUDENT_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_by_username_or_email(*args, **kwargs)


def get_course_instructor_role():
    """
    Wrapper for `student.roles.CourseInstructorRole`
    """
    backend_function = settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_STUDENT_BACKEND
    backend = import_module(backend_function)

    return backend.CourseInstructorRole


def get_course_staff_role():
    """
    Wrapper for `student.roles.CourseStaffRole`
    """
    backend_function = settings.PLATFORM_PLUGIN_ELM_CREDENTIALS_STUDENT_BACKEND
    backend = import_module(backend_function)

    return backend.CourseStaffRole


CourseInstructorRole = get_course_instructor_role()
CourseStaffRole = get_course_staff_role()
