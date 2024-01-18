"""Utility functions for the ELM credentials API."""
from datetime import datetime
from typing import Tuple

from django.utils import timezone
from rest_framework import status
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


def api_field_errors(
    field_errors: dict, status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    """
    Build a response with field errors.

    Args:
        field_errors (dict): Errors to return.
        status_code (int, optional): Status code to return. Defaults to
            status.HTTP_400_BAD_REQUEST.

    Returns:
        Response: Response with field errors.
    """
    return Response(data={"field_errors": field_errors}, status=status_code)


def api_error(error: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    """
    Build a response with an error.

    Args:
        error (str): Error to return.
        status_code (int, optional): Status code to return. Defaults to
            status.HTTP_400_BAD_REQUEST.

    Returns:
        Response: Response with an error.
    """
    return Response(data={"error": [error]}, status=status_code)
