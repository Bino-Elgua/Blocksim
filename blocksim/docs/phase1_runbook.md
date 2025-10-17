# Phase 1 Runbook: BlockSim Drone Chain (FINAL)

## Pre-Flight Checklist
- [ ] Set `DEPLOYER_API_KEY` env var (master_key_phase1)
- [ ] Charge all batteries (full 4.2V/cell)
- [ ] Calibrate GPS (open sky, 5min, >8 satellites)
- [ ] Test 1 drone end-to-end before fleet deployment

## Daily Ops (Weeks 5-6)
1. Load mission: A(0,0,20m) → B(50m,0,20m) → Land
2. Arm via app, launch (monitor telemetry live)
3. Auto-log via rsync (Pi → server every 5min)
4. Submit via BlockSim UI: Drag "Chain Submit" block
5. Check reward/slash in dashboard

## Economics (Rebalanced)
- Base reward: **0.3 tokens/flight**
- Slash: **10% of stake** (if anomaly >0.15)
- ROI (honest, 50 flights): **+140%** (14 tokens on 10 stake)
- ROI (cheater, 1 slash): **-50%** (-5 tokens)

## ML Calibration (Week 7)
```bash
python scripts/calibrate_anomalies.py \
  --good-files flight_001.csv flight_002.csv \
  --bad-files fake_001.csv fake_002.csv
```
Target: AUC >0.92, TPR 93%, FPR <5%

## Troubleshooting
- **Race condition error**: Check `chain_service._lock` active
- **Device limit exceeded**: Max 5/wallet enforced
- **Stale log rejected**: Submit within 1hr of flight
- **Unauthorized deployer**: Check `DEPLOYER_API_KEY` matches

## Emergency Contacts
- Hardware failures: Order spares (20% buffer)
- ML false positives: Lower threshold to 0.10
- Chain corruption: Restart from genesis (backup SQLite)

Version: v1.1 | Updated: Oct 16, 2025 (Ọbàtálá Audit)
