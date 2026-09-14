"""AGI_SDK listing for JuniorGaia. Spine lives in JuniorLLM."""
from __future__ import annotations

PORT = {
    "name": "JuniorGaia",
    "kind": "companion-spine",
    "quant": "ternary-1.58",
    "download_gb": 0.0,
    "protocol": "goldend-osai-omega/1",
    "schemas": [
        "junior://osai/gaia.system",
        "junior://osai/golden",
        "junior://omega/job",
    ],
    "companion_ui": "JuniorHome/ui/gaia.html",
    "dash_ui": "JuniorHome/ui/dash.html",
    "viewport": {"portrait": [1080, 1920], "landscape": [1920, 1080], "optional": True},
    "omega_job": "dash-viewport",
    "ue5_launch": False,
}


def list_gaia() -> dict:
    return dict(PORT)
