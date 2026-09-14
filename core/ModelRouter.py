# AGI_SDK - ModelRouter

PORTS = [
    "JuniorBitNetFieldCore",
    "JuniorAstra",
    "JuniorBitNetDraft",
    "JuniorGaia",
    "JuniorFable",
    "JuniorOSai",
]


class ModelRouter:
    def __init__(self):
        self.profiles = {
            "apple_silicon": {"precision": "ternary", "max_size": "70B"},
            "jetson": {"precision": "int4", "max_size": "30B"},
            "solana_mobile": {"precision": "int4", "max_size": "13B"},
        }

    def list_ports(self):
        return list(PORTS)

    def route(self, task, hardware="apple_silicon"):
        t = (task or "").lower()
        profile = self.profiles.get(hardware, self.profiles["apple_silicon"])
        port = "JuniorGaia" if any(k in t for k in ("gaia", "companion", "portrait", "goldend")) else PORTS[1]
        return {
            "port": port,
            "profile": profile,
            "ue5_launch": False,
            "omega_mesh": "stub",
            "compute": "JuniorLLM",
        }
