from fastapi.testclient import TestClient

from tvde_qr.main import app


client = TestClient(app)


def test_get_driver_page_ok():
    r = client.get("/m/demo")
    assert r.status_code == 200
    assert "Motorista TVDE" in r.text or "motorista" in r.text.lower()


def test_post_quote_uses_manual_distance_when_provided():
    r = client.post(
        "/quote",
        data={"origin": "A", "destination": "B", "distance_km": "10"},
    )
    assert r.status_code == 200
    # Deve aparecer 10 km na página
    assert "10" in r.text
    # Deve aparecer o símbolo de moeda (config padrão)
    assert "€" in r.text


def test_post_quote_works_without_manual_distance():
    r = client.post(
        "/quote",
        data={"origin": "Origem", "destination": "Destino", "distance_km": ""},
    )
    assert r.status_code == 200
    assert "€" in r.text
