from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # DB
    database_url: str = "postgresql+psycopg://tvde:tvde_pass@localhost:5432/tvde_qr"

    # Google Maps
    google_maps_api_key: str = ""
    google_maps_language: str = "pt-BR"
    google_maps_region: str = "br"

    # WhatsApp
    whatsapp_number: str = "SEUNUMERO"

    # Pricing
    currency: str = "€"
    base_fare: float = 3.0
    price_per_km: float = 0.9
    minimum_fare: float = 6.0


settings = Settings()
