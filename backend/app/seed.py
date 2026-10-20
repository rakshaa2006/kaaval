"""Seed the local synthetic organization, owner, and invoice fixtures."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import AppEnv, get_settings
from app.db.base import SessionLocal, create_tables
from app.auth.security import hash_password
from app.models import Organization, SourceDocument, User


DEMO_OWNER_EMAIL = "owner@example.test"
DEMO_OWNER_PASSWORD = "kaaval-demo-only"
DEMO_ORGANIZATION_NAME = "Mangaluru Cashew Traders"
FIXTURE_KEYS = ("supplier-invoice-clean", "supplier-invoice-poisoned")
_FIXTURES_DIRECTORY = Path(__file__).resolve().parents[2] / "fixtures" / "invoices"


@dataclass(frozen=True)
class SeedResult:
    organization_id: str
    owner_id: str
    fixture_keys: tuple[str, ...]


def _load_fixture(fixture_directory: Path, fixture_key: str) -> tuple[bytes, dict[str, object]]:
    fixture_path = fixture_directory / f"{fixture_key}.json"
    content = fixture_path.read_bytes()
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError(f"Fixture {fixture_path} must contain a JSON object.")
    metadata = parsed.get("_meta")
    if not isinstance(metadata, dict) or metadata.get("is_synthetic") is not True:
        raise ValueError(f"Fixture {fixture_path} must be explicitly marked synthetic.")
    return content, metadata


def seed_synthetic_data(
    db: Session,
    fixture_directory: Path | None = None,
) -> SeedResult:
    """Idempotently add synthetic seed records to the caller's transaction."""
    settings = get_settings()
    if settings.app_env != AppEnv.SYNTHETIC_DEMO:
        raise RuntimeError("Synthetic seed data is only allowed in SYNTHETIC_DEMO.")
    if not settings.database_url.lower().startswith("sqlite"):
        raise RuntimeError("Synthetic seed data is restricted to local SQLite.")

    fixtures_path = fixture_directory or _FIXTURES_DIRECTORY
    organization = db.scalar(
        select(Organization).where(
            Organization.name == DEMO_ORGANIZATION_NAME,
            Organization.environment == AppEnv.SYNTHETIC_DEMO.value,
        )
    )
    if organization is None:
        organization = Organization(
            name=DEMO_ORGANIZATION_NAME,
            environment=AppEnv.SYNTHETIC_DEMO.value,
            is_active=True,
        )
        db.add(organization)
        db.flush()
    else:
        organization.is_active = True

    owner = db.scalar(select(User).where(User.email == DEMO_OWNER_EMAIL))
    if owner is None:
        owner = User(
            organization_id=organization.id,
            email=DEMO_OWNER_EMAIL,
            password_hash=hash_password(DEMO_OWNER_PASSWORD),
            role="OWNER_ADMIN",
            status="ACTIVE",
            is_active=True,
        )
        db.add(owner)
    elif owner.organization_id != organization.id:
        raise RuntimeError(
            "The synthetic demo owner email is already assigned to another organization."
        )
    else:
        owner.role = "OWNER_ADMIN"
        owner.status = "ACTIVE"
        owner.is_active = True
    db.flush()

    for fixture_key in FIXTURE_KEYS:
        content, metadata = _load_fixture(fixtures_path, fixture_key)
        source_document = db.scalar(
            select(SourceDocument).where(
                SourceDocument.organization_id == organization.id,
                SourceDocument.fixture_key == fixture_key,
            )
        )
        if source_document is None:
            source_document = SourceDocument(
                organization_id=organization.id,
                fixture_key=fixture_key,
                content_hash=hashlib.sha256(content).hexdigest(),
                trust_level=str(metadata["trust_level"]),
                is_synthetic=True,
                description=str(metadata["description"]),
            )
            db.add(source_document)
        else:
            source_document.content_hash = hashlib.sha256(content).hexdigest()
            source_document.trust_level = str(metadata["trust_level"])
            source_document.is_synthetic = True
            source_document.description = str(metadata["description"])

    db.flush()
    return SeedResult(
        organization_id=organization.id,
        owner_id=owner.id,
        fixture_keys=FIXTURE_KEYS,
    )


def main() -> None:
    """Create the schema and seed the local SQLite database."""
    create_tables()
    with SessionLocal.begin() as db:
        result = seed_synthetic_data(db)
    print(
        f"Seeded synthetic organization {result.organization_id}, owner "
        f"{DEMO_OWNER_EMAIL}, and {len(result.fixture_keys)} invoice fixtures."
    )


if __name__ == "__main__":
    main()
