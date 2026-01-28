from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class OSRMRoute:
    distance_km: float
    duration_min: float


class OSRMError(RuntimeError):
    pass


class OSRMClient:
    """
    Roteamento gratuito usando:
    - Nominatim (OpenStreetMap) para geocoding (endereço -> lat/lon)
    - OSRM público para rota (lat/lon -> distância/tempo)

    Observação: serviços públicos têm rate limit. Para produção, ideal hospedar o próprio.
    """
    BASE_OSRM = "https://router.project-osrm.org"
    NOMINATIM = "https://nominatim.openstreetmap.org/search"

    def __init__(self, user_agent: str = "tvde-qr/1.0") -> None:
        self.user_agent = user_agent

    async def _get_json(self, url: str, *, params: dict, headers: dict) -> object:
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                r = await c.get(url, params=params, headers=headers)
                r.raise_for_status()
                return r.json()
        except (httpx.TimeoutException, httpx.HTTPError, ValueError) as e:
            # ValueError cobre JSONDecodeError e outros problemas de parse
            raise OSRMError(str(e)) from e

    async def _geocode_one(self, query: str) -> tuple[float, float]:
        params = {"q": query, "format": "json", "limit": 1}
        headers = {"User-Agent": self.user_agent}

        data = await self._get_json(self.NOMINATIM, params=params, headers=headers)

        if not isinstance(data, list) or not data:
            raise OSRMError(f"Endereço não encontrado: {query}")

        try:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
        except (KeyError, TypeError, ValueError) as e:
            raise OSRMError("Resposta inválida do Nominatim") from e

        return lat, lon

    async def route_by_addresses(self, origin: str, destination: str) -> OSRMRoute:
        origin = origin.strip()
        destination = destination.strip()
        if not origin or not destination:
            raise OSRMError("Origem e destino obrigatórios")

        o_lat, o_lon = await self._geocode_one(origin)
        d_lat, d_lon = await self._geocode_one(destination)

        # OSRM espera "lon,lat;lon,lat"
        url = f"{self.BASE_OSRM}/route/v1/driving/{o_lon},{o_lat};{d_lon},{d_lat}"
        params = {"overview": "false"}
        headers = {"User-Agent": self.user_agent}

        data = await self._get_json(url, params=params, headers=headers)

        if not isinstance(data, dict) or data.get("code") != "Ok":
            raise OSRMError("Falha ao calcular rota (OSRM)")

        routes = data.get("routes")
        if not isinstance(routes, list) or not routes:
            raise OSRMError("Falha ao calcular rota (OSRM): rota vazia")

        try:
            distance_m = float(routes[0]["distance"])
            duration_s = float(routes[0]["duration"])
        except (KeyError, TypeError, ValueError) as e:
            raise OSRMError("Resposta inválida do OSRM") from e

        return OSRMRoute(
            distance_km=round(distance_m / 1000.0, 2),
            duration_min=round(duration_s / 60.0, 1),
        )
