from __future__ import annotations

from datetime import timedelta, datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from tvde_qr.models import RouteCache


class RouteCacheRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_recent(
        self,
        origin: str,
        destination: str,
        max_age: timedelta,
    ) -> RouteCache | None:
        """
        Retorna rota se existir e não estiver expirada.
        """
        stmt = (
            select(RouteCache)
            .where(RouteCache.origin == origin)
            .where(RouteCache.destination == destination)
            .order_by(RouteCache.created_at.desc())
            .limit(1)
        )

        result = self.session.execute(stmt).scalar_one_or_none()
        if not result:
            return None

        if datetime.utcnow() - result.created_at.replace(tzinfo=None) > max_age:
            return None

        return result

    def save(
        self,
        origin: str,
        destination: str,
        distance_km: float,
        duration_min: float | None,
        source: str,
    ) -> RouteCache:
        route = RouteCache(
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            duration_min=duration_min,
            source=source,
        )
        self.session.add(route)
        self.session.commit()
        self.session.refresh(route)
        return route
