# Space Biology Knowledge Engine - Frontend (Angular)

## Prerequisites
- Node.js 18+
- FastAPI backend running on `http://localhost:8000`

## Install
```bash
cd frontend
npm install
```

## Run (dev)
```bash
npm start
```
This uses `proxy.conf.json` to forward `/search` and `/health` to the backend.

## Build (prod)
```bash
npm run build
```
Outputs to `dist/space-bio-frontend`.

## Use
1. Start the backend: `python main.py`
2. Start the frontend: `npm start` (inside `frontend/`)
3. Open `http://localhost:4200`, enter a question, and click Search.

## Config
- Proxy: `frontend/proxy.conf.json`
- Angular config: `frontend/angular.json`
