# Tech Titans — Blockchain Investigation Platform (MVP)

Problem Statement 26183 · Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges

This repository is a runnable MVP scaffold focused on the core investigation path: submit a wallet, load clearly-labelled demo data (or query Etherscan when configured), inspect a transaction graph, review evidence-backed candidate attribution, create/update a case, and export a report. It deliberately does **not** claim integration with NCRP, SAHYOG, exchanges, or law-enforcement systems.

## Architecture
- `frontend/`: React + Vite + TypeScript, responsive dark investigator UI, Cytoscape graph, dashboard, wallet investigation, cases, report export.
- `backend/`: FastAPI API, NetworkX path analysis, optional Etherscan V2 adapter, explainable rule-based indicators.
- `backend/schema.sql`: PostgreSQL starter schema. The demo API uses an in-memory repository so it runs without a database; see persistence note below.

## Requirements
- Node.js 20+ and npm
- Python 3.11+
- Optional: PostgreSQL 15+ and an Etherscan API key

## Run locally
### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; on macOS/Linux use: cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs for API documentation.

### 2. Frontend
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the local URL printed by Vite. The frontend expects the API at `http://localhost:8000` by default; set `VITE_API_BASE_URL` in `frontend/.env` to override.

## Data modes
- **Demo mode (default):** realistic-looking but synthetic transactions. The UI and API label them as demonstration data. Never present them as actual blockchain evidence.
- **Etherscan mode (optional):** configure `ETHERSCAN_API_KEY` in `backend/.env`. Requests use Etherscan API V2 (`chainid=1`, Ethereum mainnet). Public API plans have rate/feature limits. The API key stays on the server. If the provider fails, the API returns an explicit error rather than silently replacing live results with demo results.
- Other chains are currently demo-only. Cross-chain attribution and bridge tracing are not implemented.

## Security and limitations
This is a hackathon MVP, **not production-ready for real victim or law-enforcement data**. Authentication is a local demo gate only; it is not a secure identity provider. Do not enter real personal, complaint, or confidential case information. Before real deployment, implement OIDC/MFA, server-side RBAC on every endpoint, CSRF/session strategy, encrypted secrets and evidence storage, durable PostgreSQL repositories/migrations, rate limits, retention controls, backups, monitoring, and an independent security review.

Attribution is a *candidate* based on a demo label or configured source. A wallet label does not prove ownership or wrongdoing. The risk rules are explainable heuristics, not a legal conclusion or validated ML model.

## Tests
```bash
cd backend
pip install -r requirements.txt
pytest
```

## API overview
- `GET /health`
- `POST /api/investigations` — `{ "address": "0x...", "network": "ethereum", "mode": "demo" }`
- `GET /api/cases`
- `POST /api/cases`
- `PATCH /api/cases/{case_id}`
- `GET /api/reports/{investigation_id}.json`
- `GET /api/reports/{investigation_id}.csv`

## Suggested next sprint
1. Add Alembic migrations and a PostgreSQL repository implementation.
2. Replace demo login with an approved institutional identity provider and enforce roles in backend dependencies.
3. Add signed evidence manifests and immutable audit storage.
4. Add Bitcoin adapter and attribution source registry with provenance and verification dates.
5. Add integration tests against a controlled provider fixture before enabling live queries.
