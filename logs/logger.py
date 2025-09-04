import json
import os
from datetime import datetime, timezone

LOG_FILE = "logs/access.log"

def write_log(data: dict):
    """Append logs as JSON to access.log"""
    os.makedirs("logs", exist_ok=True)  # ensure folder exists
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
