# AGI_SDK - ModelRouter

class ModelRouter:
    def __init__(self):
        self.profiles = {
            "apple_silicon": {"precision": "ternary", "max_size": "70B"},
            "jetson": {"precision": "int4", "max_size": "30B"},
            "solana_mobile": {"precision": "int4", "max_size": "13B"}
        }

    def route(self, task, hardware="apple_silicon"):
        return self.profiles.get(hardware, self.profiles["apple_silicon"])