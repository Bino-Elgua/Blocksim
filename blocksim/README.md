# BlockSim Phase1 Launch Package

This folder contains the Phase 1 launch package for BlockSim. It includes a minimal backend (FastAPI), frontend stubs, ML calibration script, and Docker configuration for local testing.

Quick start (from repo root):

```bash
cd blocksim
docker-compose up --build
```

The backend will be available at http://localhost:8000 and exposes endpoints under `/api/chain`.

Run the calibrator (locally, not in docker):

```bash
python3 scripts/calibrate_anomalies.py
```
