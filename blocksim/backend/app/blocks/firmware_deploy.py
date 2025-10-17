from typing import Dict, Any
from app.chain_service import chain_service
import hashlib
import os

AUTHORIZED_DEPLOYER_KEY = os.getenv("DEPLOYER_API_KEY", "master_key_phase1")

def firmware_deploy(inputs: dict, params: dict, dt: float) -> dict:
    firmware_version = params.get("firmware_version", "v1.0")
    target_drones = params.get("target_drones", ["drone_001"])
    julia_code = inputs.get("julia_script", "")
    deployer_key = params.get("deployer_key", "")
    
    if deployer_key != AUTHORIZED_DEPLOYER_KEY:
        return {
            "error": "unauthorized_deployer",
            "deployments": {},
            "deployed_count": 0
        }
    
    firmware_hash = hashlib.sha256(julia_code.encode()).hexdigest()
    
    deployments = {}
    for device_id in target_drones:
        try:
            chain_service.register_firmware(
                version=firmware_version,
                pcr=f"pcr_{firmware_version}",
                binary_sha256=firmware_hash
            )
            deployments[device_id] = {
                "status": "deployed",
                "firmware_hash": firmware_hash,
                "version": firmware_version
            }
        except Exception as e:
            deployments[device_id] = {"status": "failed", "error": str(e)}
    
    return {
        "deployments": deployments,
        "firmware_hash": firmware_hash,
        "deployed_count": sum(1 for d in deployments.values() if d["status"] == "deployed")
    }
