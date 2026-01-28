from __future__ import annotations

from dataclasses import dataclass
import httpx


@dataclass(frozen=True)
class GoogleRoute:
    distance_km: float
    duration_min: float
    origin_formatted: str | None = None
    destination_formatted: str | None = None


class GoogleMapsError(RuntimeError):
    pass


class GoogleMapsClient:
    def __init__(self, api_key: str, language: str = "pt-BR", region: str = "br") -> None:
        self.api_key = api_key
        self.language = language
        self.region = region

    async def route_by_addresses(self, origin: str, destination: str) -> GoogleRoute:
        if not self.api_key:
            raise GoogleMapsError("GOOGLE_MAPS_API_KEY não configurada")

        origin = origin.strip()
        destination = destination.strip()
        if not origin or not destination:
            raise GoogleMapsError("Origem e destino obrigatórios")

        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "driving",
            "language": self.language,
            "region": self.region,
            "key": self.api_key,
        }

        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.get(url, params=params)
            data = r.json()

        status = data.get("status")
        if status != "OK":
            raise GoogleMapsError(data.get("error_message") or status or "Directions falhou")

        routes = data.get("routes") or []
        if not routes:
            raise GoogleMapsError("Directions: nenhuma rota")

        legs = routes[0].get("legs") or []
        if not legs:
            raise GoogleMapsError("Directions: legs vazio")

        total_m = sum(int(l["distance"]["value"]) for l in legs)
        total_s = sum(int(l["duration"]["value"]) for l in legs)

        return GoogleRoute(
            distance_km=round(total_m / 1000.0, 2),
            duration_min=round(total_s / 60.0, 1),
            origin_formatted=legs[0].get("start_address"),
            destination_formatted=legs[-1].get("end_address"),
        )
