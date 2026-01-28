from __future__ import annotations


class DistanceService:
    """
    Estimativa simples (mock) sem mapa.
    Depois você troca por Haversine (lat/lon) ou API (Google/Mapbox).
    """

    def estimate_km(self, origin: str, destination: str) -> float:
        origin = (origin or "").strip()
        destination = (destination or "").strip()

        if not origin or not destination:
            raise ValueError("Origem e destino são obrigatórios")

        # Mock previsível: evita 0 km e dá algo consistente.
        base = abs(len(origin) - len(destination)) + 5
        return round(float(base), 1)
