from typing import Dict, Any
from app.chain_service import chain_service
import time

def chain_submit(inputs: dict, params: dict, dt: float) -> dict:
    device_id = params.get("device_id", "drone_001")
    wallet_id = params.get("wallet_id", "wallet_test")
    stake_amount = params.get("stake_amount", 10.0)
    firmware_version = params.get("firmware_version", "v1.0")
    sim_log = inputs.get("sim_log", {})
    
    try:
        # Check 1: Sufficient stake
        if not chain_service.has_sufficient_stake(wallet_id, stake_amount):
            return {"status": "rejected", "reason": "insufficient_stake"}
        
        # Check 2: Device registration + Sybil cap
        if device_id not in chain_service.device_registry:
            if not chain_service.register_device(wallet_id, device_id):
                return {"status": "rejected", "reason": "device_limit_exceeded"}
        elif chain_service.device_registry[device_id]["wallet"] != wallet_id:
            return {"status": "rejected", "reason": "device_wallet_mismatch"}
        
        # Check 3: Attestation
        attestation = {
            "device_id": device_id,
            "firmware_version": firmware_version,
            "pcr": f"pcr_{firmware_version}",
            "nonce": str(time.time())
        }
        if not chain_service.verify_attestation(device_id, attestation):
            return {"status": "rejected", "reason": "invalid_attestation"}
        
        # Check 4: Submit log (timestamp enforced internally)
        log_payload = {
            "device_id": device_id,
            "log": sim_log.get("log", []),
            "log_hash": sim_log.get("log_hash", ""),
            "log_signature": sim_log.get("log_signature", ""),
            "attestation": attestation,
            "submitted_at": time.time()
        }
        
        accepted, msg = chain_service.submit_log(device_id, log_payload)
        if not accepted:
            return {"status": "rejected", "reason": msg}
        
        # Check 5: Anomaly detection (adjusted threshold)
        anomaly_score = chain_service.check_anomalies(log_payload)
        if anomaly_score > 0.15:
            chain_service.slash_stake(wallet_id, 0.10, f"Anomaly {anomaly_score:.2f}")
            return {"status": "flagged", "anomaly_score": anomaly_score}
        
        # Mining + Reward (rebalanced to 0.3)
        block_mined = chain_service.mine_pending_block()
        reward = 0.3
        chain_service.reward(wallet_id, reward)
        
        return {
            "status": "success",
            "block_hash": chain_service.get_latest_block_hash() if block_mined else None,
            "reward": reward,
            "anomaly_score": anomaly_score
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}
