"""AGI_SDK listing for JuniorGaia. Spine lives in JuniorLLM."""
from __future__ import annotations

PORT = {
    "name": "JuniorGaia",
    "kind": "companion-spine",
    "quant": "ternary-1.58",
    "download_gb": 0.0,
    "portrait": "JuniorHome/ui/gaia.html",
    "omega_mesh": "stub",
    "ue5_launch": False,
    "likeness": "original-goldend",
}


def list_gaia() -> dict:
    return dict(PORT)
