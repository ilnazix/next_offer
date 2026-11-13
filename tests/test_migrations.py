from sqlalchemy import create_engine, inspect, text

from app.migrations import run_schema_migrations


def test_startup_migration_upgrades_a_pre_banner_offers_table():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(
            text("CREATE TABLE products (id INTEGER PRIMARY KEY, code VARCHAR(64))")
        )
        connection.execute(
            text(
                """
                CREATE TABLE offers (
                    id INTEGER PRIMARY KEY,
                    client_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    trigger_type VARCHAR(128) NOT NULL,
                    message_text TEXT,
                    status VARCHAR(32) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )

    run_schema_migrations(engine)

    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("offers")}
    assert {"banner_template_id", "event_id", "shown_at", "responded_at"} <= columns
    assert inspector.has_table("banner_templates")

    engine.dispose()


def test_startup_migration_is_idempotent():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(
            text("CREATE TABLE products (id INTEGER PRIMARY KEY, code VARCHAR(64))")
        )
        connection.execute(
            text(
                """
                CREATE TABLE offers (
                    id INTEGER PRIMARY KEY,
                    client_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    trigger_type VARCHAR(128) NOT NULL,
                    status VARCHAR(32) DEFAULT 'pending'
                )
                """
            )
        )

    run_schema_migrations(engine)
    run_schema_migrations(engine)

    engine.dispose()
