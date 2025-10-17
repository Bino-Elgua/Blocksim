from app.sim_chain import SimpleValidationChain, EconomicLayer
from typing import Tuple, Dict, Any
import threading
import time

class ChainService:
    def __init__(self):
        self.chain = SimpleValidationChain()
        self.economics = EconomicLayer(self.chain)
        self.device_registry = {}
        self._lock = threading.RLock()
        self._wallet_devices = {}

    def register_firmware(self, version: str, pcr: str, binary_sha256: str) -> None:
        with self._lock:
            self.chain.firmware_registry.register_firmware(version, pcr, binary_sha256)

    def verify_attestation(self, device_id: str, attestation: Dict[str, Any]) -> bool:
        with self._lock:
            firmware_version = attestation.get("firmware_version")
            return self.chain.attestation_verifier.verify_quote(attestation, firmware_version)

    def submit_log(self, device_id: str, log_payload: Dict[str, Any]) -> Tuple[bool, str]:
        with self._lock:
            submitted_at = log_payload.get("submitted_at", 0)
            if time.time() - submitted_at > 3600:
                return False, "stale_log"
            return self.chain.submit_log(device_id, log_payload)

    def check_anomalies(self, log_payload: Dict[str, Any]) -> float:
        with self._lock:
            return self.chain.check_anomalies(log_payload)

    def slash_stake(self, wallet_id: str, percentage: float, reason: str) -> None:
        with self._lock:
            self.economics.slash(wallet_id, reason, percentage)

    def reward(self, wallet_id: str, amount: float) -> None:
        with self._lock:
            self.economics.reward(wallet_id, amount)

    def has_sufficient_stake(self, wallet_id: str, amount: float) -> bool:
        with self._lock:
            return self.economics.stakes.get(wallet_id, 0) >= amount

    def register_device(self, wallet_id: str, device_id: str) -> bool:
        with self._lock:
            if wallet_id not in self._wallet_devices:
                self._wallet_devices[wallet_id] = set()
            if len(self._wallet_devices[wallet_id]) >= 5:
                return False
            self._wallet_devices[wallet_id].add(device_id)
            self.device_registry[device_id] = {"wallet": wallet_id}
            return True

    def mine_pending_block(self) -> bool:
        with self._lock:
            return self.chain.mine_block()

    def get_latest_block_hash(self) -> str:
        with self._lock:
            return self.chain.chain[-1]["block_hash"] if self.chain.chain else None

chain_service = ChainService()
