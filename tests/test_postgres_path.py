import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="set TEST_DATABASE_URL to run the PostgreSQL test path",
)


def test_database_fixture_targets_postgres(engine):
    assert engine.dialect.name == "postgresql"
