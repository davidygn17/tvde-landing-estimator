from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from tvde_qr.db import Base


class RouteCache(Base):
    __tablename__ = "route_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    origin: Mapped[str] = mapped_column(Text, nullable=False)
    destination: Mapped[str] = mapped_column(Text, nullable=False)

    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    duration_min: Mapped[float | None] = mapped_column(Float, nullable=True)

    source: Mapped[str] = mapped_column(String(32), nullable=False, default="google_directions")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
