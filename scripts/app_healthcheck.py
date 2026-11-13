import os
import sys
import urllib.request

url = os.environ.get("APP_HEALTH_URL", "http://localhost:8000/health")

try:
    with urllib.request.urlopen(url, timeout=3) as response:
        print(response.read().decode())
except Exception as error:
    print(f"app healthcheck failed: {error}", file=sys.stderr)
    raise SystemExit(1)

raise SystemExit(0)
