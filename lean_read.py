import json
from pathlib import Path
p = Path.home() / ".juniorhome" / "os" / "lean.json"
print(json.dumps(json.loads(p.read_text()) if p.exists() else {"ok": False, "port": "AGI_SDK", "writes": 0}))
