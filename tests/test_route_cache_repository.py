from datetime import timedelta

import pytest

from tvde_qr.db import SessionLocal
from tvde_qr.repositories.route_cache import RouteCacheRepository


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_save_and_get_recent_route(db_session):
    repo = RouteCacheRepository(db_session)

    repo.save(
        origin="A",
        destination="B",
        distance_km=12.3,
        duration_min=20.0,
        source="test",
    )

    cached = repo.get_recent(
        "A",
        "B",
        max_age=timedelta(hours=1),
    )

    assert cached is not None
    assert cached.distance_km == 12.3
    assert cached.source == "test"
