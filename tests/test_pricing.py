import pytest

from tvde_qr.services.pricing import PricingConfig, PricingService


def test_pricing_basic():
    svc = PricingService(PricingConfig(currency="€", base_fare=3.0, price_per_km=1.0, minimum_fare=0.0))
    assert svc.calculate_price(10) == 13.0


def test_pricing_minimum_fare_applies():
    svc = PricingService(PricingConfig(currency="€", base_fare=0.0, price_per_km=0.1, minimum_fare=6.0))
    assert svc.calculate_price(10) == 6.0


def test_pricing_negative_distance_raises():
    svc = PricingService(PricingConfig())
    with pytest.raises(ValueError):
        svc.calculate_price(-1)
