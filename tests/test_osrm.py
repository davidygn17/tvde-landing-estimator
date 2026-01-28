import httpx
import pytest
import respx

from tvde_qr.services.osrm import OSRMClient, OSRMError


@pytest.mark.asyncio
@respx.mock
async def test_osrm_route_by_addresses_ok():
    # Endpoints usados pelo OSRMClient
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    osrm_url = "https://router.project-osrm.org/route/v1/driving/-7.8892,37.0145;-9.1355,38.7742"

    # Mock geocoding (origem)
    respx.get(
        nominatim_url,
        params={"q": "Aeroporto de Faro", "format": "json", "limit": 1},
    ).mock(
        return_value=httpx.Response(
            200,
            json=[{"lat": "37.0145", "lon": "-7.8892"}],
        )
    )

    # Mock geocoding (destino)
    respx.get(
        nominatim_url,
        params={"q": "Aeroporto de Lisboa", "format": "json", "limit": 1},
    ).mock(
        return_value=httpx.Response(
            200,
            json=[{"lat": "38.7742", "lon": "-9.1355"}],
        )
    )

    # Mock rota OSRM
    respx.get(
        osrm_url,
        params={"overview": "false"},
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "code": "Ok",
                "routes": [{"distance": 278_500.0, "duration": 10_200.0}],  # metros / segundos
            },
        )
    )

    client = OSRMClient(user_agent="tvde-qr-test")
    route = await client.route_by_addresses("Aeroporto de Faro", "Aeroporto de Lisboa")

    assert route.distance_km == 278.5
    assert route.duration_min == 170.0


@pytest.mark.asyncio
@respx.mock
async def test_osrm_geocode_not_found_raises():
    nominatim_url = "https://nominatim.openstreetmap.org/search"

    respx.get(
        nominatim_url,
        params={"q": "Lugar Inexistente 123", "format": "json", "limit": 1},
    ).mock(
        return_value=httpx.Response(200, json=[])
    )

    client = OSRMClient(user_agent="tvde-qr-test")

    with pytest.raises(OSRMError):
        await client.route_by_addresses("Lugar Inexistente 123", "Aeroporto de Lisboa")


@pytest.mark.asyncio
@respx.mock
async def test_osrm_route_error_raises():
    nominatim_url = "https://nominatim.openstreetmap.org/search"

    # Origem ok
    respx.get(nominatim_url, params={"q": "A", "format": "json", "limit": 1}).mock(
        return_value=httpx.Response(200, json=[{"lat": "0", "lon": "0"}])
    )
    # Destino ok
    respx.get(nominatim_url, params={"q": "B", "format": "json", "limit": 1}).mock(
        return_value=httpx.Response(200, json=[{"lat": "0", "lon": "1"}])
    )

    # OSRM espera lon,lat;lon,lat -> origem (0,0) destino (lon=1, lat=0)
    osrm_url = "https://router.project-osrm.org/route/v1/driving/0.0,0.0;1.0,0.0"
    respx.get(osrm_url, params={"overview": "false"}).mock(
        return_value=httpx.Response(200, json={"code": "InvalidQuery"})
    )

    client = OSRMClient(user_agent="tvde-qr-test")

    with pytest.raises(OSRMError):
        await client.route_by_addresses("A", "B")


@pytest.mark.asyncio
async def test_osrm_empty_origin_or_destination():
    client = OSRMClient(user_agent="tvde-qr-test")

    with pytest.raises(OSRMError):
        await client.route_by_addresses("", "Lisboa")

    with pytest.raises(OSRMError):
        await client.route_by_addresses("Faro", "")


@pytest.mark.asyncio
@respx.mock
async def test_osrm_geocode_http_error():
    # Simula erro do Nominatim
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=httpx.Response(500)
    )

    client = OSRMClient(user_agent="tvde-qr-test")

    with pytest.raises(OSRMError):
        await client.route_by_addresses("Faro", "Lisboa")


@pytest.mark.asyncio
@respx.mock
async def test_osrm_timeout():
    # Simula timeout do httpx
    respx.get("https://nominatim.openstreetmap.org/search").side_effect = httpx.TimeoutException(
        "timeout"
    )

    client = OSRMClient(user_agent="tvde-qr-test")

    with pytest.raises(OSRMError):
        await client.route_by_addresses("Faro", "Lisboa")


@pytest.mark.asyncio
@respx.mock
async def test_osrm_empty_routes():
    nominatim_url = "https://nominatim.openstreetmap.org/search"

    respx.get(nominatim_url, params={"q": "A", "format": "json", "limit": 1}).mock(
        return_value=httpx.Response(200, json=[{"lat": "0", "lon": "0"}])
    )
    respx.get(nominatim_url, params={"q": "B", "format": "json", "limit": 1}).mock(
        return_value=httpx.Response(200, json=[{"lat": "1", "lon": "1"}])
    )

    # OSRM: origem lon=0 lat=0; destino lon=1 lat=1
    osrm_url = "https://router.project-osrm.org/route/v1/driving/0.0,0.0;1.0,1.0"
    respx.get(osrm_url, params={"overview": "false"}).mock(
        return_value=httpx.Response(200, json={"code": "Ok", "routes": []})
    )

    client = OSRMClient(user_agent="tvde-qr-test")

    with pytest.raises(OSRMError):
        await client.route_by_addresses("A", "B")
