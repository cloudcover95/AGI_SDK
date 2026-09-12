"""AGI capsule display emit. Host lives in JuniorOmega/blender/jc_blender.py.

Does not import bpy. Capsules here are topology only.
"""
from __future__ import annotations

from pathlib import Path

JOB = "agi-capsule"
OMEGA = Path(__file__).resolve().parents[2] / "JuniorOmega" / "blender" / "jc_blender.py"


def capsule_cmd(out_dir: str = "blender_out", trit: int = 0) -> list[str]:
    return ["python3", str(OMEGA), JOB, out_dir, str(trit)]


if __name__ == "__main__":
    print(" ".join(capsule_cmd()))
