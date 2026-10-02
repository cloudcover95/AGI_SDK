"""AGI workflow step. Computes trit energy if Home has not."""
from __future__ import annotations

import json
from pathlib import Path

PATH = Path.home() / ".juniorhome" / "os" / "trit_mesh.json"


def step(note: str = "AGI_SDK") -> dict:
    if PATH.exists():
        row = json.loads(PATH.read_text(encoding="utf-8"))
        return {"step": "trit-energy", "energy": row.get("energy"), "source": "home", "svd_1024": False}
    xs = [((ord(c) % 5) - 2) / 2.0 for c in note[:32]] or [0.0]
    gamma = sum(abs(x) for x in xs) / len(xs) or 1.0
    zeros = sum(1 for x in xs if int(round(x / gamma)) == 0)
    return {"step": "trit-energy", "energy": round(1.0 - zeros / len(xs), 3), "source": "local", "svd_1024": False, "model_pull": False}


if __name__ == "__main__":
    print(json.dumps(step(), indent=2))
