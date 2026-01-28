import pytest

from tvde_qr.services.distance import DistanceService


def test_distance_estimate_returns_positive_number():
    svc = DistanceService()
    km = svc.estimate_km("Origem", "Destino")
    assert km > 0


def test_distance_estimate_requires_origin_and_destination():
    svc = DistanceService()
    with pytest.raises(ValueError):
        svc.estimate_km("", "Destino")
    with pytest.raises(ValueError):
        svc.estimate_km("Origem", "")
