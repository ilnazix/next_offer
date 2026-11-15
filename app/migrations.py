"""Idempotent startup schema migrations.

``migrations/init.sql`` only runs when PostgreSQL initialises an empty volume.
Existing demo volumes therefore never receive the additive columns and tables
added after the first launch. ``run_schema_migrations`` is executed by the API
and the worker on startup and applies those changes to an already-populated
database.

The function inspects the live database first, so it is safe to run on every
boot and safe to run concurrently from the app and worker processes.
"""

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.constants import OFFER_STATUS_VALUES
from app.models import Base, Offer

logger = logging.getLogger(__name__)

OFFERS_TABLE = "offers"
BANNER_TEMPLATES_TABLE = "banner_templates"

ADDITIVE_OFFER_COLUMNS = (
    "banner_template_id",
    "event_id",
    "title",
    "subtitle",
    "shown_at",
    "responded_at",
)


def _sql_in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


def _add_missing_columns(engine: Engine, existing_columns: set[str]) -> None:
    offer_table = Offer.__table__
    with engine.begin() as connection:
        for name in ADDITIVE_OFFER_COLUMNS:
            if name in existing_columns:
                continue
            column = offer_table.c[name]
            type_sql = column.type.compile(dialect=engine.dialect)
            connection.execute(
                text(f"ALTER TABLE {OFFERS_TABLE} ADD COLUMN {name} {type_sql}")
            )
            logger.info("Added missing column offers.%s", name)


def _apply_postgres_constraints(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        return

    statuses = _sql_in_list(OFFER_STATUS_VALUES)
    with engine.begin() as connection:
        connection.execute(
            text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint
                        WHERE conname = 'offers_banner_template_id_fkey'
                    ) THEN
                        ALTER TABLE offers
                            ADD CONSTRAINT offers_banner_template_id_fkey
                            FOREIGN KEY (banner_template_id)
                            REFERENCES banner_templates(id);
                    END IF;
                END $$;
                """
            )
        )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_offers_event_id "
                "ON offers(event_id)"
            )
        )
        connection.execute(
            text("ALTER TABLE offers DROP CONSTRAINT IF EXISTS offers_status_check")
        )
        connection.execute(
            text(
                f"ALTER TABLE offers ADD CONSTRAINT offers_status_check "
                f"CHECK (status IN ({statuses}))"
            )
        )


def run_schema_migrations(engine: Engine) -> None:
    """Bring an existing database up to the current additive schema."""

    inspector = inspect(engine)
    if not inspector.has_table(OFFERS_TABLE):
        # Fresh databases rely on migrations/init.sql.
        return

    if not inspector.has_table(BANNER_TEMPLATES_TABLE):
        Base.metadata.tables[BANNER_TEMPLATES_TABLE].create(
            bind=engine, checkfirst=True
        )
        logger.info("Created missing table %s", BANNER_TEMPLATES_TABLE)
        inspector = inspect(engine)

    existing_columns = {
        column["name"] for column in inspector.get_columns(OFFERS_TABLE)
    }
    _add_missing_columns(engine, existing_columns)

    try:
        _apply_postgres_constraints(engine)
    except Exception:  # pragma: no cover - depends on legacy data
        logger.exception("Could not refresh offer constraints on startup")
