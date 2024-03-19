""" This module is used to import the edxapp_wrapper module. """
from platform_plugin_elm_credentials.edxapp_wrapper.authentication import BearerAuthenticationAllowInactiveUser
from platform_plugin_elm_credentials.edxapp_wrapper.certificates import GeneratedCertificate
from platform_plugin_elm_credentials.edxapp_wrapper.enrollments import get_user_enrollments
from platform_plugin_elm_credentials.edxapp_wrapper.modulestore import modulestore
from platform_plugin_elm_credentials.edxapp_wrapper.student import (
    CourseInstructorRole,
    CourseStaffRole,
    get_user_by_username_or_email,
)
