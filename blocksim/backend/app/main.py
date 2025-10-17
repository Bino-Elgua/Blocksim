from fastapi import FastAPI, APIRouter, Body
from app.chain_service import chain_service
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BlockSim Phase1 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()


@router.post("/stake")
async def stake_tokens(wallet_id: str = Body(...), amount: float = Body(...)):
    if chain_service.economics.stake(wallet_id, amount):
        return {"status": "staked", "amount": amount}
    return {"status": "error", "reason": "stake_failed"}


@router.post("/deploy_firmware")
async def deploy_firmware_endpoint(device_id: str = Body(...), firmware_version: str = Body(...), deployer_key: str = Body(...)):
    # Minimal endpoint to register firmware for a device
    try:
        chain_service.register_firmware(firmware_version, f"pcr_{firmware_version}", "manual_deploy")
        return {"status": "ok", "device_id": device_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}


app.include_router(router, prefix="/api/chain", tags=["Chain"])
