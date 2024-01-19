"""Builds ELM credentials."""
from platform_plugin_elm_credentials.api.serializers import (
    Address,
    AwardedBy,
    AwardingBody,
    CountryCode,
    CredentialSubject,
    DeliveryDetails,
    DisplayParameter,
    HasClaim,
    Issuer,
    Location,
    PrimaryLanguage,
)
from platform_plugin_elm_credentials.api.utils import get_fullname, to_iso_format


class CredentialBuilder:
    """
    Builds ELM credentials for a user based on a given course and certificate.

    This class provides a convenient way to construct ELM credentials for a user who has
    successfully completed a specified course and received a certificate of completion.

    Attributes:
        course (CourseOverview): The course for which credentials are being built.
        user (User): The user for whom credentials are being built.
        certificate (GeneratedCertificate): The certificate associated with the user's completion of the course.
        additional_params (dict): Additional parameters for the credential.

    Properties:
        full_name (str): The full name of the user.

    Methods:
        build() -> dict:
            Constructs and returns the ELM credential in the form of a dictionary.
    """

    def __init__(self, course, user, certificate, additional_params):
        self.course = course
        self.user = user
        self.certificate = certificate
        self.additional_params = additional_params

    @property
    def full_name(self) -> str:
        """
        Get the full name of the user.

        Returns:
            str: The full name of the user.
        """
        return self.user.profile.name

    def build(self) -> dict:
        """
        Build the credential.

        Returns:
            dict: The constructed ELM credential in dictionary format.
        """
        given_name, family_name = get_fullname(self.full_name)

        awarding_body = AwardingBody(
            alt_label={"en": self.course.org},
            legal_name={"en": self.course.org},
            location=Location(address=Address(country_code=CountryCode())),
        )
        awarded_by = AwardedBy(
            awarding_body=awarding_body,
            awarding_date=to_iso_format(self.certificate.created_date),
        )
        has_claim = HasClaim(
            awarded_by=awarded_by,
            title={
                "en": f"Course certificate for passing {self.course.display_name} course"
            },
        )
        credential_subject = CredentialSubject(
            given_name={"en": given_name},
            family_name={"en": family_name},
            full_name={"en": self.full_name},
            has_claim=has_claim,
        )
        display_parameter = DisplayParameter(
            primary_language=PrimaryLanguage(), title={"en": self.course.display_name}
        )
        issuer = Issuer(
            alt_label={"en": self.course.org},
            legal_name={"en": self.course.org},
        )
        delivery_details = DeliveryDetails(delivery_address=self.user.email)

        return {
            "credential": {
                "issuer": issuer,
                "credential_subject": credential_subject,
                "expiration_date": self.additional_params.get("expired_at"),
                "valid_until": self.additional_params.get("expired_at"),
                "display_parameter": display_parameter,
            },
            "delivery_details": delivery_details,
        }