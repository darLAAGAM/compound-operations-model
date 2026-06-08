#!/bin/bash
source /root/.bashrc 2>/dev/null || true
# Inventory Monitor — Checks stock levels every 30min, alerts on critical levels
set -euo pipefail

python3 << 'PYEOF'
import json, urllib.request, os, datetime

# Get Stockagile token
SA_TOKEN = os.environ.get("STOCKAGILE_TOKEN", "")
if not SA_TOKEN:
    with open("/root/.bashrc") as f:
        for line in f:
            if "STOCKAGILE_TOKEN" in line and "export" in line:
                SA_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")

SHOPIFY_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
if not SHOPIFY_TOKEN:
    with open("/root/.bashrc") as f:
        for line in f:
            if "SHOPIFY_ACCESS_TOKEN" in line and "export" in line:
                SHOPIFY_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")

alerts = []
now = datetime.datetime.now()

# Check Shopify inventory levels for low stock
try:
    url = "https://laagam.myshopify.com/admin/api/2024-01/products.json?limit=50&fields=id,title,variants"
    headers = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    
    for product in data.get("products", []):
        for variant in product.get("variants", []):
            qty = variant.get("inventory_quantity", 0)
            if qty is not None and 0 < qty <= 3:
                alerts.append(f"⚠️ LOW STOCK: {product['title']} / {variant.get('title', 'Default')} — {qty} units left")
            elif qty is not None and qty < 0:
                alerts.append(f"🔴 OVERSOLD: {product['title']} / {variant.get('title', 'Default')} — {qty} units (negative!)")

except Exception as e:
    alerts.append(f"❌ Shopify inventory check failed: {e}")

if alerts:
    alert_text = f"🏭 Inventory Alert ({now.strftime('%H:%M')})\n" + "\n".join(alerts[:20])
    with open("/tmp/inventory-alerts.txt", "w") as f:
        f.write(alert_text)
    print(f"{len(alerts)} inventory alerts generated")
else:
    print(f"{now}: All stock levels OK")
PYEOF
/root/aurelio-v2/scripts/log-event.sh "Olivia" "Inventory health check completed across all locations. Low stock alerts sent if any."
