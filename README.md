# 🚖 TVDE Landing + Estimativa de Viagem

Site mobile-first para motoristas TVDE: o cliente lê um QR Code, abre uma 
landing premium e pode pedir uma estimativa de viagem em tempo real.

## ✨ Features

- Landing page premium via QR Code (mobile-first)
- Estimativa de distância e tempo por rota real
- Geocoding gratuito com OpenStreetMap (Nominatim)
- Cálculo de rota com OSRM (sem custos de API)
- Cache de rotas no PostgreSQL com TTL
- Migrations com Alembic
- Testes com pytest + coverage (mocks do OSRM)

## 🧱 Stack

- **Python 3.11+** + **FastAPI**
- **Jinja2** (templates HTML)
- **httpx** (requisições async)
- **PostgreSQL** via Docker
- **SQLAlchemy** + **Alembic**
- **pytest** + pytest-cov + respx + pytest-asyncio
- **Poetry** para gestão de dependências

## 🚀 Como rodar localmente

```bash
git clone https://github.com/davidygn17/tvde-landing-estimator.git
cd tvde-landing-estimator
poetry install
docker-compose up -d
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

## 🧪 Testes

```bash
poetry run pytest --cov=src
```

## 📌 Requisitos

- Python 3.11+
- Poetry
- Docker Desktop
