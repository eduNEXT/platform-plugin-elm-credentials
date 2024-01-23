"""Builds ELM credentials."""
from uuid import uuid4

from django.conf import settings

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
        course_block (CourseBlock): The course for which credentials are being built.
        user (User): The user for whom credentials are being built.
        certificate (GeneratedCertificate): The certificate associated with the user's completion of the course.
        additional_params (dict): Additional parameters for the credential.
        elm_credential_defaults (dict): Default values for the credential.

    Properties:
        full_name (str): The full name of the user.
        primary_language (PrimaryLanguage): The primary language of the credential.
        org_country_code (CountryCode): The country code of the organisation in the credential.
        issuer (Issuer): The issuer of the credential.

    Methods:
        build() -> dict:
            Constructs and returns the ELM credential in the form of a dictionary.
    """

    LANGUAGE_CODE_MAP = {
        "en": "ENG",
        "es": "SPA",
    }
    PRIMARY_LANGUAGE = "SPA"
    ORG_COUNTRY_CODE = "ESP"

    def __init__(self, course_block, user, certificate, additional_params):
        self.course_block = course_block
        self.user = user
        self.certificate = certificate
        self.additional_params = additional_params
        self.credential_settings = self.course_block.other_course_settings.get(
            "ELM_CREDENTIALS_DEFAULTS", {}
        ) or getattr(settings, "ELM_CREDENTIALS_DEFAULTS", {})

    @property
    def full_name(self) -> str:
        """
        Get the full name of the user.

        Returns:
            str: The full name of the user.
        """
        return self.user.profile.name

    @property
    def primary_language(self) -> PrimaryLanguage:
        """
        Get the primary language of the credential.

        First, the primary language is retrieved from the course settings. If it is not found,
        the primary language is retrieved from the Django setting. If it is not found,
        use the default primary language.

        If you want to use a language code other than those in `LANGUAGE_CODE_MAP`, you can
        add a `primary_language_map` dictionary to the `ELM_CREDENTIALS_DEFAULTS` setting.

        Returns:
            PrimaryLanguage: The primary language of the credential.
        """
        primary_language_code = self.credential_settings.get("primary_language_code")
        primary_language_map = self.credential_settings.get("primary_language_map", {})

        self.LANGUAGE_CODE_MAP.update(primary_language_map)

        maped_primary_language = primary_language_code or self.LANGUAGE_CODE_MAP.get(
            getattr(settings, "LANGUAGE_CODE", "en"), self.PRIMARY_LANGUAGE
        )
        return PrimaryLanguage(id=maped_primary_language)

    @property
    def org_country_code(self) -> CountryCode:
        """
        Get the country code of the organisation in the credential.

        First, the country code is retrieved from the course settings. If it is not found,
        the primary language is retrieved from the Django setting. If it is not found,
        use the default country code.

        Returns:
            CountryCode: The country code of the credential.
        """
        org_country_code = self.credential_settings.get("org_country_code")
        return CountryCode(id=org_country_code or self.ORG_COUNTRY_CODE)

    @property
    def issuer(self) -> Issuer:
        """
        Get the issuer of the credential.

        Returns:
            Issuer: The issuer of the credential.
        """
        issuer_id = self.credential_settings.get("issuer_id")
        return Issuer(
            id=issuer_id or str(uuid4()),
            alt_label={"en": self.course_block.org},
            legal_name={"en": self.course_block.org},
        )

    def build(self) -> dict:
        """
        Build the credential.

        Returns:
            dict: The constructed ELM credential in dictionary format.
        """
        given_name, family_name = get_fullname(self.full_name)

        awarding_body = AwardingBody(
            alt_label={"en": self.course_block.org},
            legal_name={"en": self.course_block.org},
            location=Location(address=Address(country_code=self.org_country_code)),
        )
        awarded_by = AwardedBy(
            awarding_body=awarding_body,
            awarding_date=to_iso_format(self.certificate.created_date),
        )
        has_claim = HasClaim(
            awarded_by=awarded_by,
            title={
                "en": f"Course certificate for passing {self.course_block.display_name} course"
            },
        )
        credential_subject = CredentialSubject(
            given_name={"en": given_name},
            family_name={"en": family_name},
            full_name={"en": self.full_name},
            has_claim=has_claim,
        )
        display_parameter = DisplayParameter(
            primary_language=self.primary_language,
            title={"en": self.course_block.display_name},
        )
        delivery_details = DeliveryDetails(delivery_address=self.user.email)

        return {
            "credential": {
                "issuer": self.issuer,
                "credential_subject": credential_subject,
                "expiration_date": self.additional_params.get("expires_at"),
                "valid_until": self.additional_params.get("expires_at"),
                "display_parameter": display_parameter,
            },
            "delivery_details": delivery_details,
        }
