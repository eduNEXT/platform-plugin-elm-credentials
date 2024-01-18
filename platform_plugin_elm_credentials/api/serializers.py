"""Pydantic models for ELMv3 data."""
from typing import List
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from platform_plugin_elm_credentials.api.utils import get_current_datetime, to_camel


class ConfigModel(BaseModel):
    """Pydantic model with custom configuration."""

    model_config = ConfigDict(alias_generator=to_camel)


class AwardingBody(ConfigModel):
    """Pydantic model for ELMv3 awarding body."""

    id: str = "urn:epass:org:1"
    type: str = "Organisation"
    alt_label: dict = Field(validation_alias="alt_label")
    legal_name: dict = Field(validation_alias="legal_name")


class AwardedBy(ConfigModel):
    """Pydantic model for ELMv3 AwardedBy property."""

    id: str = "urn:epass:awardingProcess:1"
    type: str = "AwardingProcess"
    awarding_body: AwardingBody = Field(validation_alias="awarding_body")
    awarding_date: str = Field(validation_alias="awarding_date")


class HasClaim(ConfigModel):
    """Pydantic model for ELMv3 HasClaim property."""

    id: str = "urn:epass:learningAchievement:1"
    type: str = "LearningAchievement"
    awarded_by: AwardedBy = Field(validation_alias="awarded_by")
    title: dict = Field(validation_alias="title")


class CredentialSubject(ConfigModel):
    """Pydantic model for ELMv3 CredentialSubject property."""

    id: str = "urn:epass:person:1"
    type: str = "Person"
    given_name: dict = Field(validation_alias="given_name")
    family_name: dict = Field(validation_alias="family_name")
    full_name: dict = Field(validation_alias="full_name")
    has_claim: HasClaim = Field(validation_alias="has_claim")


class DeliveryDetails(ConfigModel):
    """Pydantic model for ELMv3 DeliveryDetails property."""

    delivery_address: str = Field(validation_alias="delivery_address")


class Issuer(ConfigModel):
    """Pydantic model for ELMv3 Issuer property."""

    id: str = Field(default=f"urn:epass:org:{uuid4()}")
    type: str = "Organisation"
    alt_label: dict = Field(validation_alias="alt_label")
    legal_name: dict = Field(validation_alias="legal_name")


class ELMv3DataModel(ConfigModel):
    """Pydantic model for ELMv3 data."""

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
    valid_from: str = Field(default_factory=get_current_datetime)
    valid_until: str = Field(default_factory=get_current_datetime)
    expiration_date: str = Field(default_factory=get_current_datetime)
    issuance_date: str = Field(default_factory=get_current_datetime)
    issued: str = Field(default_factory=get_current_datetime)
    issuer: Issuer = Field(validation_alias="issuer")
    credential_subject: CredentialSubject = Field(validation_alias="credential_subject")
    delivery_details: DeliveryDetails = Field(validation_alias="delivery_details")
