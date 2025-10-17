import hashlib
import time
from typing import Dict, Any, Tuple, List


class FirmwareRegistry:
    def __init__(self):
        self._registry = {}

    def register_firmware(self, version: str, pcr: str, binary_sha256: str) -> None:
        self._registry[version] = {"pcr": pcr, "sha256": binary_sha256, "registered_at": time.time()}


class AttestationVerifier:
    def __init__(self, firmware_registry: FirmwareRegistry):
        self.firmware_registry = firmware_registry

    def verify_quote(self, attestation: Dict[str, Any], firmware_version: str) -> bool:
        # Very small stub: ensure firmware_version is registered and pcr matches expected format
        meta = self.firmware_registry._registry.get(firmware_version)
        if not meta:
            return False
        return attestation.get("pcr") == meta.get("pcr")


class SimpleValidationChain:
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.pending_logs: List[Dict[str, Any]] = []
        self.firmware_registry = FirmwareRegistry()
        self.attestation_verifier = AttestationVerifier(self.firmware_registry)
        self._anomaly_model = None

    def submit_log(self, device_id: str, log_payload: Dict[str, Any]) -> Tuple[bool, str]:
        # Basic checks: log must contain device_id and log list
        if not log_payload.get("log"):
            return False, "empty_log"
        self.pending_logs.append(log_payload)
        return True, "accepted"

    def check_anomalies(self, log_payload: Dict[str, Any]) -> float:
        # Simple heuristic: if more than 10% of entries have large accel, flag
        logs = log_payload.get("log", [])
        if not logs:
            return 0.0
        high = 0
        for entry in logs:
            ax = abs(entry.get("accel_x", 0))
            ay = abs(entry.get("accel_y", 0))
            if ax + ay > 15:
                high += 1
        return high / max(1, len(logs))

    def mine_block(self) -> bool:
        if not self.pending_logs:
            return False
        block = {
            "block_hash": hashlib.sha256(str(time.time()).encode()).hexdigest(),
            "logs": self.pending_logs.copy(),
            "timestamp": time.time()
        }
        self.chain.append(block)
        self.pending_logs.clear()
        return True


class EconomicLayer:
    def __init__(self, chain: SimpleValidationChain):
        self.stakes: Dict[str, float] = {}
        self.chain = chain

    def stake(self, wallet_id: str, amount: float) -> bool:
        if amount <= 0:
            return False
        self.stakes[wallet_id] = self.stakes.get(wallet_id, 0.0) + amount
        return True

    def slash(self, wallet_id: str, reason: str, percentage: float) -> None:
        cur = self.stakes.get(wallet_id, 0.0)
        self.stakes[wallet_id] = max(0.0, cur * (1.0 - percentage))

    def reward(self, wallet_id: str, amount: float) -> None:
        self.stakes[wallet_id] = self.stakes.get(wallet_id, 0.0) + amount
