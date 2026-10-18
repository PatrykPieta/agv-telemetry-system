"""Freshness of a process heartbeat (written only after a successful poll/send)."""
from pathlib import Path
import sys
import time
path = Path(sys.argv[1])
sys.exit(0 if path.exists() and time.time() - path.stat().st_mtime < 30 else 1)
