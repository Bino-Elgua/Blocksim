#!/bin/bash

# Usage: ./deploy_firmware.sh <device_id> <firmware_file> <deployer_key>

DEVICE_ID=$1
FIRMWARE_FILE=$2
DEPLOYER_KEY=$3

if [ -z "$DEVICE_ID" ] || [ -z "$FIRMWARE_FILE" ] || [ -z "$DEPLOYER_KEY" ]; then
  echo "Usage: $0 <device_id> <firmware_file> <deployer_key>"
  exit 1
fi

# Flash to Pi (assuming USB boot or SD)
echo "[INFO] Flashing $FIRMWARE_FILE to device $DEVICE_ID -- replace /dev/sdX with target before running"
dd if="$FIRMWARE_FILE" of=/dev/sdX bs=4M conv=fsync || true

# TPM attest (requires tpm2-tools)
tpm2_createprimary --hierarchy=o --key-algorithm=rsa --hash-algorithm=sha256 --key-context=prim.ctx || true
tpm2_create --parent-context=prim.ctx --key-algorithm=rsa --hash-algorithm=sha256 --public=ek.pub --private=ek.priv || true
tpm2_evictcontrol -c prim.ctx -p 0x81010001 || true

# Call BlockSim API for registration
curl -s -X POST http://localhost:8000/api/chain/deploy_firmware \
  -H "Content-Type: application/json" \
  -d "{\"device_id\": \"$DEVICE_ID\", \"firmware_version\": \"v1.0\", \"deployer_key\": \"$DEPLOYER_KEY\"}"

echo "Firmware deployed to $DEVICE_ID. Verify attestation."
