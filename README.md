# TVDE QR — Landing + Estimativa de Viagem (FastAPI) + Postgres Cache

Site minimalista (mobile-first) para motorista TVDE: o cliente lê um QR Code no cartão, abre uma landing premium e pode pedir uma estimativa rápida de viagem (origem/destino).  
O sistema calcula distância/tempo por rota real **gratuitamente** usando **OpenStreetMap (Nominatim) + OSRM**, e faz **cache no PostgreSQL** para evitar chamadas repetidas.

## ✨ Features

- Landing page premium para abrir via QR (mobile-first)
- Formulário: origem/destino → distância + tempo (rota real)
- Cache de rota no PostgreSQL (TTL)
- Migrations com Alembic
- Testes com pytest + coverage (inclui mocks do OSRM)
- Projeto organizado com Poetry e `src/` layout

## 🧱 Stack

- Python + FastAPI
- Jinja2 (templates)
- httpx (requests)
- PostgreSQL (Docker)
- SQLAlchemy + Alembic
- pytest + pytest-cov + respx + pytest-asyncio

---

## ✅ Requisitos

- Python 3.11+ (recomendado)
- Poetry
- Docker Desktop (para PostgreSQL)

---

## 🚀 Como rodar localmente

### 1) Clonar e instalar dependências

```bash
git clone <SEU_REPO_AQUI>
cd tvde-qr
poetry install
