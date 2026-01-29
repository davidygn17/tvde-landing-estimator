from __future__ import annotations

from datetime import timedelta
from urllib.parse import quote

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from tvde_qr.db import SessionLocal
from tvde_qr.repositories.route_cache import RouteCacheRepository
from tvde_qr.services.distance import DistanceService
from tvde_qr.services.pricing import PricingConfig, PricingService
from tvde_qr.settings import settings
from tvde_qr.services.osrm import OSRMClient, OSRMError

osrm = OSRMClient()


app = FastAPI(title="TVDE QR")

@app.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    # Página principal do QR (link do cartão)
    return templates.TemplateResponse("driver.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    return HTMLResponse("OK")


@app.get("/health")
def health():
    return {"ok": True}


app.mount("/static", StaticFiles(directory="src/tvde_qr/web/static"), name="static")
templates = Jinja2Templates(directory="src/tvde_qr/web/templates")

distance_service = DistanceService()

pricing_service = PricingService(
    PricingConfig(
        currency=settings.currency,
        base_fare=settings.base_fare,
        price_per_km=settings.price_per_km,
        minimum_fare=settings.minimum_fare,
    )
)

def get_db():
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL não configurada")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/m/demo", response_class=HTMLResponse)
def driver_demo(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("driver.html", {"request": request})


@app.post("/quote", response_class=HTMLResponse)
async def quote_page(
    request: Request,
    origin: str = Form(...),
    destination: str = Form(...),
    distance_km: str = Form(""),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    origin_clean = origin.strip()
    destination_clean = destination.strip()

    repo = RouteCacheRepository(db)

    # -------------------------
    # A3.1: KM manual (se o cliente informar)
    # -------------------------
    km: float | None = None
    duration_min: float | None = None
    distance_source = "estimated"

    if distance_km and distance_km.strip():
        try:
            km = float(distance_km.strip().replace(",", "."))
            if km > 0:
                distance_source = "manual_km"
        except ValueError:
            km = None

    if km is not None:
        repo.save(
            origin=origin_clean,
            destination=destination_clean,
            distance_km=km,
            duration_min=None,
            source=distance_source,
        )

    else:
        # -------------------------
        # A3.2: Cache (24h)
        # -------------------------
        cached = repo.get_recent(
            origin_clean,
            destination_clean,
            max_age=timedelta(hours=24),
        )

        if cached:
            km = cached.distance_km
            duration_min = cached.duration_min
            distance_source = f"cache:{cached.source}"

        else:
            try:
                route = await osrm.route_by_addresses(origin_clean, destination_clean)
                km = route.distance_km
                duration_min = route.duration_min
                distance_source = "osrm"
            

                repo.save(
                    origin=origin_clean,
                    destination=destination_clean,
                    distance_km=km,
                    duration_min=duration_min,
                    source=distance_source,
                )
                
            except OSRMError:
                km = None
                duration_min = None
                distance_source = "unavailable"
                
            
                
    # Se não foi possível calcular distância real e o usuário não informou km,
    # retornamos uma resposta honesta (sem estourar erro).
    if km is None:
        currency = pricing_service.config.currency
        msg = (
            "Olá! Vi seu QR e queria um orçamento.\n"
            "Não consegui calcular a rota automaticamente agora.\n"
            f"Origem: {origin_clean}\n"
            f"Destino: {destination_clean}\n"
            "Pode me confirmar a morada completa ou informar os km aproximados?"
        )
        whatsapp_url = f"https://wa.me/{settings.whatsapp_number}?text={quote(msg)}"

        return templates.TemplateResponse(
            "quote_result.html",
            {
                "request": request,
                "origin": origin_clean,
                "destination": destination_clean,
                "distance_km": None,
                "duration_min": None,
                "price": None,
                "currency": currency,
                "distance_source": distance_source,
                "whatsapp_url": whatsapp_url,
            },
        )

    # preço
    price = pricing_service.calculate_price(km)
    currency = pricing_service.config.currency

    msg = (
        f"Olá! Vi seu QR e queria confirmar o valor.\n"
        f"Origem: {origin_clean}\n"
        f"Destino: {destination_clean}\n"
        f"Distância: {km} km ({distance_source})\n"
        f"Estimativa: {currency} {price}\n"
        f"Horário: "
    )
    whatsapp_url = f"https://wa.me/{settings.whatsapp_number}?text={quote(msg)}"

    return templates.TemplateResponse(
        "quote_result.html",
        {
            "request": request,
            "origin": origin_clean,
            "destination": destination_clean,
            "distance_km": km,
            "duration_min": duration_min,
            "price": price,
            "currency": currency,
            "distance_source": distance_source,
            "whatsapp_url": whatsapp_url,
        },
    )
