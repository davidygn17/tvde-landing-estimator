from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PricingConfig:
    currency: str = "€"
    base_fare: float = 3.00
    price_per_km: float = 0.90
    minimum_fare: float = 6.00


class PricingService:
    def __init__(self, config: PricingConfig) -> None:
        self.config = config

    def calculate_price(self, distance_km: float) -> float:
        if distance_km < 0:
            raise ValueError("Distância inválida")

        price = self.config.base_fare + (distance_km * self.config.price_per_km)
        if price < self.config.minimum_fare:
            price = self.config.minimum_fare

        return round(price, 2)
