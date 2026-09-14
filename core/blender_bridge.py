"""AGI capsule display emit. Host lives in JuniorOmega/blender/jc_blender.py.

Does not import bpy. Capsules here are topology only.
Gaia mesh OBJ is written by JuniorLLM ports.gaia_mesh — this only points at it.
"""
from __future__ import annotations

from pathlib import Path

JOB = "agi-capsule"
GAIA_JOB = "gaia-spine"
OMEGA = Path(__file__).resolve().parents[2] / "JuniorOmega" / "blender" / "jc_blender.py"
GAIA_OBJ = Path.home() / ".juniorhome" / "gaia_mesh" / "gaia_spine.obj"


def capsule_cmd(out_dir: str = "blender_out", trit: int = 0) -> list[str]:
    return ["python3", str(OMEGA), JOB, out_dir, str(trit)]


def gaia_cmd() -> list[str]:
    py = Path.home() / ".juniorhome" / "gaia_mesh" / "gaia_blender.py"
    return ["blender", "--background", "--python", str(py)]


def gaia_obj() -> str:
    return str(GAIA_OBJ)


if __name__ == "__main__":
    print(" ".join(capsule_cmd()))
    print(" ".join(gaia_cmd()))
