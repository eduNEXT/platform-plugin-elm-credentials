"""Utility functions for the ELM credentials API."""
from datetime import datetime
from typing import Tuple

from django.utils import timezone
from rest_framework.response import Response


def get_current_datetime() -> str:
    """
    Returns the current datetime.

    Returns:
        datetime: The current datetime.
    """
    return to_iso_format(timezone.now())


def to_iso_format(date: datetime) -> str:
    """
    Returns the date in ISO format.
        Example: 2024-01-01T01:02:03+00:00

    Args:
        date (datetime): The date to convert.

    Returns:
        str: The date in ISO format.
    """
    return date.isoformat(timespec="seconds")


def to_camel(string: str) -> str:
    """
    Returns a string in camel case.

    Args:
        string (str): String to convert.

    Returns:
        str: String in camel case.
    """
    words = string.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


def get_fullname(name: str) -> Tuple[str, str]:
    """
    Returns the first and last name from a full name.

    Args:
        name (str): Full name.

    Returns:
        Tuple[str, str]: First and last name.
    """
    first_name, last_name = "", ""

    if name:
        fullname = name.split(" ", 1)
        first_name = fullname[0]

        if fullname[1:]:
            last_name = fullname[1]

    return first_name, last_name


def get_filename(course_id: str, user=None) -> str:
    """
    Get the filename for the specified course ID and user.

    Args:
        course_id (str): The unique identifier for the course.
        user (User, optional): The user object. Defaults to None.

    Returns:
        str: The filename
    """
    course_id = course_id.replace(":", "_")
    if not user:
        return f"credentials-{course_id}.zip"
    return f"credential-{user}-{course_id}.json"


def api_field_errors(field_errors: dict, status_code: int) -> Response:
    """
    Build a response with field errors.

    Args:
        field_errors (dict): Errors to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with field errors.
    """
    return Response(data={"field_errors": field_errors}, status=status_code)


def api_error(error: str, status_code: int) -> Response:
    """
    Build a response with an error.

    Args:
        error (str): Error to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with an error.
    """
    return Response(data={"error": [error]}, status=status_code)


def pydantic_error_to_response(errors: list) -> dict:
    """
    Build a dictionary as of Pydantic errors.

    Args:
        errors (list): Errors of Pydantic.

    Returns:
        dict: serialized Pydantic errors
    """
    return {error["loc"][0]: error["msg"] for error in errors}
