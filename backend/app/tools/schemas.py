"""Validated Pydantic argument schemas for the mock tool registry."""
from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


FixtureKey = Literal["supplier-invoice-clean", "supplier-invoice-poisoned"]


class ReadInvoiceArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fixture_key: FixtureKey = "supplier-invoice-clean"


class SendEmailArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination: str = Field(min_length=3, max_length=320)
    template: Literal["supplier_invoice_reminder"]

    @field_validator("destination")
    @classmethod
    def require_synthetic_destination(cls, value: str) -> str:
        normalized = value.strip().lower()
        local_part, separator, domain = normalized.partition("@")
        valid_address = re.fullmatch(
            r"[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
            r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
            r"(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)*\.example\.test",
            normalized,
        )
        if (
            not separator
            or not local_part
            or not domain.endswith(".example.test")
            or valid_address is None
        ):
            raise ValueError("Destination must use a synthetic .example.test address.")
        return normalized


class DeleteBackupArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backup_id: str = Field(pattern=r"^synthetic-backup-[a-z0-9-]{1,64}$")
