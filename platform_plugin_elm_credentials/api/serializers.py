"""Pydantic models for ELMv3 data."""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from platform_plugin_elm_credentials.api.utils import get_current_datetime, to_camel, to_iso_format


class QueryParamsModel(BaseModel):
    """Pydantic model for query parameters.

    The purpose of this model is to validate the query parameters and
    convert them to the appropriate type.
    """

    username: str
    expires_at: Optional[datetime] = None
    to_file: bool = True

    @field_serializer("expires_at")
    def to_iso_format(self, value) -> Optional[str]:
        if value:
            return to_iso_format(value)
        return value


class ConfigModel(BaseModel):
    """Pydantic model with custom configuration.

    The purpose of this model is to set the custom configuration for all
    the models that inherit from it.

    The custom configuration is set to:
        * alias_generator: to_camel (converts the field names from snake_case to camelCase)
    """

    model_config = ConfigDict(alias_generator=to_camel)


class CountryCode(ConfigModel):
    """Pydantic model for ELMv3 country code.

    Stores the country code of the organisation in the format required by ELMv3.
    This property is used in the Address model.
    """

    id: str
    type: str = "Concept"
    in_scheme: dict = Field(
        default={
            "id": "http://publications.europa.eu/resource/authority/country",
            "type": "ConceptScheme",
        },
        validation_alias="in_scheme",
    )
    notation: str = "country"

    @field_serializer("id")
    def get_id(self, value):
        return f"http://publications.europa.eu/resource/authority/country/{value}"


class Address(ConfigModel):
    """Pydantic model for ELMv3 address.

    Stores the address of the organisation in the format required by ELMv3.
    This property is used in the Location model.
    """

    id: str = "urn:epass:address:1"
    type: str = "Address"
    country_code: CountryCode = Field(validation_alias="country_code")


class Location(ConfigModel):
    """Pydantic model for ELMv3 location.

    Stores the location of the organisation in the format required by ELMv3.
    This property is used in the AwardingBody model.
    """

    id: str = "urn:epass:location:1"
    type: str = "Location"
    address: Address = Field(validation_alias="address")


class AwardingBody(ConfigModel):
    """Pydantic model for ELMv3 awarding body.

    Stores the awarding body of the credential in the format required by ELMv3.
    This property is used in the AwardedBy model.
    """

    id: str = "urn:epass:org:1"
    type: str = "Organisation"
    alt_label: dict = Field(validation_alias="alt_label")
    legal_name: dict = Field(validation_alias="legal_name")
    location: Location = Field(validation_alias="location")


class AwardedBy(ConfigModel):
    """Pydantic model for ELMv3 AwardedBy property.

    Stores the awarded by of the credential in the format required by ELMv3.
    This property is used in the HasClaim model.
    """

    id: str = "urn:epass:awardingProcess:1"
    type: str = "AwardingProcess"
    awarding_body: AwardingBody = Field(validation_alias="awarding_body")
    awarding_date: str = Field(validation_alias="awarding_date")


class HasClaim(ConfigModel):
    """Pydantic model for ELMv3 HasClaim property.

    Stores the has claim of the credential in the format required by ELMv3.
    This property is used in the CredentialSubject model.
    """

    id: str = "urn:epass:learningAchievement:1"
    type: str = "LearningAchievement"
    awarded_by: AwardedBy = Field(validation_alias="awarded_by")
    title: dict = Field(validation_alias="title")


class PrimaryLanguage(ConfigModel):
    """Pydantic model for ELMv3 PrimaryLanguage property.

    Stores the primary language of the credential in the format required by ELMv3.
    This property is used in the DisplayParameter model.
    """

    id: str
    type: str = "Concept"
    in_scheme: dict = Field(
        default={
            "id": "http://publications.europa.eu/resource/authority/language",
            "type": "ConceptScheme",
        },
        validation_alias="in_scheme",
    )
    notation: str = "language"

    @field_serializer("id")
    def get_id(self, value):
        return f"http://publications.europa.eu/resource/authority/language/{value}"


class DisplayParameter(ConfigModel):
    """Pydantic model for ELMv3 DisplayParameter property.

    Stores the display parameter of the credential in the format required by ELMv3.
    This property is used in the ELMBodyModel model.
    """

    id: str = "urn:epass:displayParameter:1"
    type: str = "DisplayParameter"
    primary_language: PrimaryLanguage = Field(validation_alias="primary_language")
    title: dict = Field(validation_alias="title")


class CredentialSubject(ConfigModel):
    """Pydantic model for ELMv3 CredentialSubject property.

    Stores the credential subject of the credential in the format required by ELMv3.
    This property is used in the ELMBodyModel model.
    """

    id: str = "urn:epass:person:1"
    type: str = "Person"
    given_name: dict = Field(validation_alias="given_name")
    family_name: dict = Field(validation_alias="family_name")
    full_name: dict = Field(validation_alias="full_name")
    has_claim: HasClaim = Field(validation_alias="has_claim")


class Issuer(ConfigModel):
    """Pydantic model for ELMv3 Issuer property.

    Stores the issuer of the credential in the format required by ELMv3.
    This property is used in the ELMBodyModel model.
    """

    id: str
    type: str = "Organisation"
    alt_label: dict = Field(validation_alias="alt_label")
    legal_name: dict = Field(validation_alias="legal_name")

    @field_serializer("id")
    def get_id(self, value):
        return f"urn:epass:org:{value}"


class DeliveryDetails(ConfigModel):
    """Pydantic model for ELMv3 DeliveryDetails property.

    Stores the delivery details of the credential in the format required by ELMv3.
    This property is used in the ELMCredentialModel model.
    """

    delivery_address: str = Field(validation_alias="delivery_address")


class ELMBodyModel(ConfigModel):
    """Pydantic model for ELM body data.

    Stores all the data in the credential property required by ELMv3.
    """

    id: str = Field(default=f"urn:credential:{uuid4()}")
    type: List[str] = ["VerifiableCredential", "EuropeanDigitalCredential"]
    context: List[str] = Field(
        serialization_alias="@context",
        default=[
            "https://www.w3.org/2018/credentials/v1",
            "https://data.europa.eu/snb/model/context/edc-ap",
        ],
    )
    credential_schema: dict = {
        "id": "http://data.europa.eu/snb/model/ap/edc-generic-no-cv",
        "type": "ShaclValidator2017",
    }
    valid_until: Optional[str] = Field(validation_alias="valid_until")
    expiration_date: Optional[str] = Field(validation_alias="expiration_date")
    valid_from: str = Field(default_factory=get_current_datetime)
    issuance_date: str = Field(default_factory=get_current_datetime)
    issued: str = Field(default_factory=get_current_datetime)
    issuer: Issuer = Field(validation_alias="issuer")
    credential_subject: CredentialSubject = Field(validation_alias="credential_subject")
    display_parameter: DisplayParameter = Field(validation_alias="display_parameter")


class ELMCredentialModel(ConfigModel):
    """Pydantic model for ELM credential.

    Stores the ELM credential in the format required by ELMv3.
    """

    credential: ELMBodyModel = Field(validation_alias="credential")
    delivery_details: DeliveryDetails = Field(validation_alias="delivery_details")
