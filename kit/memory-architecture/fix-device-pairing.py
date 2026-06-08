#!/usr/bin/env python3
"""
fix-device-pairing.py — Fix OpenClaw device pairing for agents
Part of AgentivAI Memory Architecture Kit

Problem: Agent has device.json (identity) but missing or broken device-auth.json
Solution: Creates matching paired.json + device-auth.json with correct Ed25519 key format

Usage:
  sudo python3 fix-device-pairing.py /Users/<agent>/.openclaw

The critical detail: paired.json publicKey must be the RAW 32-byte Ed25519 key
(base64url, no padding), NOT the full DER/SPKI encoding.

PEM → DER → skip 12-byte SPKI header → last 32 bytes = raw key
"""

import json
import base64
import secrets
import time
import sys
import os

def fix_pairing(state_dir: str):
    identity_dir = os.path.join(state_dir, "identity")
    devices_dir = os.path.join(state_dir, "devices")
    
    device_path = os.path.join(identity_dir, "device.json")
    auth_path = os.path.join(identity_dir, "device-auth.json")
    paired_path = os.path.join(devices_dir, "paired.json")
    
    # Read device identity
    if not os.path.exists(device_path):
        print(f"❌ No device.json at {device_path}")
        print("   Run the gateway once to generate device identity first.")
        sys.exit(1)
    
    with open(device_path) as f:
        device = json.load(f)
    
    device_id = device["deviceId"]
    pem = device["publicKeyPem"]
    
    # Extract raw 32-byte Ed25519 public key from PEM
    der_b64 = "".join(
        line for line in pem.strip().split("\n")
        if "BEGIN" not in line and "END" not in line
    )
    der_bytes = base64.b64decode(der_b64)
    raw_key = der_bytes[-32:]  # Skip 12-byte SPKI header
    raw_b64url = base64.urlsafe_b64encode(raw_key).rstrip(b"=").decode()
    
    # Generate auth token
    token = secrets.token_urlsafe(32)
    now_ms = int(time.time() * 1000)
    
    # Create devices directory if needed
    os.makedirs(devices_dir, exist_ok=True)
    
    # Write paired.json (gateway-side)
    paired = {
        device_id: {
            "deviceId": device_id,
            "publicKey": raw_b64url,  # RAW key, not DER!
            "platform": "darwin",
            "clientId": "cli",
            "clientMode": "cli",
            "role": "operator",
            "roles": ["operator"],
            "scopes": [
                "operator.admin",
                "operator.approvals",
                "operator.pairing",
                "operator.read",
                "operator.write",
            ],
            "tokens": {
                "operator": {
                    "token": token,
                    "role": "operator",
                    "scopes": [
                        "operator.admin",
                        "operator.approvals",
                        "operator.pairing",
                    ],
                    "createdAtMs": now_ms,
                    "rotatedAtMs": now_ms,
                }
            },
            "createdAtMs": now_ms,
            "approvedAtMs": now_ms,
            "remoteIp": "127.0.0.1",
        }
    }
    
    with open(paired_path, "w") as f:
        json.dump(paired, f, indent=2)
    
    # Write device-auth.json (client-side)
    auth = {
        "version": 1,
        "deviceId": device_id,
        "tokens": {
            "operator": {
                "token": token,
                "role": "operator",
                "scopes": [
                    "operator.admin",
                    "operator.approvals",
                    "operator.pairing",
                ],
                "updatedAtMs": now_ms,
            }
        },
    }
    
    with open(auth_path, "w") as f:
        json.dump(auth, f, indent=2)
    
    # Set permissions
    os.chmod(paired_path, 0o600)
    os.chmod(auth_path, 0o600)
    
    print(f"✅ Fixed pairing for device {device_id[:16]}...")
    print(f"   Raw public key: {raw_b64url[:24]}...")
    print(f"   Token: {token[:16]}...")
    print(f"   Files: {paired_path}")
    print(f"          {auth_path}")
    print(f"")
    print(f"⚠️  Restart the gateway to load the new pairing:")
    print(f"   sudo launchctl stop ai.openclaw.<agent>")
    print(f"   sudo launchctl start ai.openclaw.<agent>")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: sudo python3 {sys.argv[0]} /Users/<agent>/.openclaw")
        sys.exit(1)
    fix_pairing(sys.argv[1])
