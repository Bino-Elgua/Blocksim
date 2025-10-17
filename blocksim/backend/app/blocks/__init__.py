BLOCK_REGISTRY = {}
BLOCK_METADATA = {}

from .firmware_deploy import firmware_deploy
from .chain_submit import chain_submit

BLOCK_REGISTRY.update({
    1000: firmware_deploy,
    1001: chain_submit
})

BLOCK_METADATA.update({
    1000: {
        "name": "Deploy Firmware",
        "category": "chain",
        "inputs": [{"name": "julia_script", "type": "string"}],
        "outputs": [{"name": "deployments", "type": "dict"}],
        "parameters": [
            {"name": "firmware_version", "type": "string", "default": "v1.0"},
            {"name": "target_drones", "type": "list", "default": ["drone_001"]},
            {"name": "deployer_key", "type": "string", "required": True}
        ]
    },
    1001: {
        "name": "Submit to Chain",
        "category": "chain",
        "inputs": [{"name": "sim_log", "type": "dict"}],
        "outputs": [
            {"name": "status", "type": "string"},
            {"name": "block_hash", "type": "string"},
            {"name": "reward", "type": "float"}
        ],
        "parameters": [
            {"name": "device_id", "type": "string", "default": "drone_001"},
            {"name": "wallet_id", "type": "string", "default": "wallet_test"},
            {"name": "stake_amount", "type": "float", "default": 10.0},
            {"name": "firmware_version", "type": "string", "default": "v1.0"}
        ]
    }
})
