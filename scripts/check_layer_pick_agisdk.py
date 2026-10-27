#!/usr/bin/env python3
"""Layer-pick and close-rule self-check for AGI_SDK (JuniorCloud LLC, additive only).

Mirrors the layer stack documented in JuniorHome docs/LAYER_STACK.md:
  T0 Python trit      for n < 512*512
  T1 bit-plane numpy  for n < 1024*1024
  T2 native C when the .so exists, otherwise falls back to T1.
Weights are trit-packed before the layer pick. No bench, no LUT, no GGUF.
Pure standard library; no network, no model pull, no servers started.
Quant ports referenced: Home, OSai, FieldCore, Flagstaff, JuniorLLM.
"""
import hashlib

RATE = 0.05
BIND = "127.0.0.1"
FLAGS = {"mint": False, "socket": False, "layer_one": False, "fetch": False, "ue5_launch": False}
PORTS = ("Home", "OSai", "FieldCore", "Flagstaff", "JuniorLLM")
T0_MAX = 512 * 512
T1_MAX = 1024 * 1024


def trit_pack(weights):
    """Map floats to trits {-1,0,1} with a RATE dead zone, packed 5 trits per byte."""
    trits = [0 if abs(w) <= RATE else (1 if w > 0 else -1) for w in weights]
    out = bytearray()
    for i in range(0, len(trits), 5):
        v = 0
        for t in reversed(trits[i:i + 5]):
            v = v * 3 + (t + 1)
        out.append(v)
    return bytes(out), trits


def layer_pick(n, so_exists=False):
    if n < T0_MAX:
        return "T0"
    if n < T1_MAX:
        return "T1"
    return "T2" if so_exists else "T1"


def close_rule(prev, pack, text):
    return hashlib.sha256(prev + pack + text.encode("utf-8")).hexdigest()[:16]


def self_check():
    assert BIND == "127.0.0.1"
    assert not any(FLAGS.values())
    assert layer_pick(0) == "T0" and layer_pick(T0_MAX - 1) == "T0"
    assert layer_pick(T0_MAX) == "T1" and layer_pick(T1_MAX - 1) == "T1"
    assert layer_pick(T1_MAX) == "T1" and layer_pick(T1_MAX, so_exists=True) == "T2"
    pack, trits = trit_pack([0.5, -0.5, 0.04, -0.05, 0.051, 0.0, -1.2])
    assert trits == [1, -1, 0, 0, 1, 0, -1]
    assert len(pack) == 2
    # Trit-pack happens before the layer pick: pick on the trit count.
    assert layer_pick(len(trits)) == "T0"
    a = close_rule(b"\x00" * 16, pack, "agisdk")
    b = hashlib.sha256(b"\x00" * 16 + pack + b"agisdk").hexdigest()[:16]
    assert a == b and len(a) == 16
    # Two engines (here: function vs inline) agree on rate and close rule.
    assert RATE == 0.05
    return {"rate": RATE, "close": a, "bind": BIND, "ports": PORTS}


if __name__ == "__main__":
    r = self_check()
    print("check_layer_pick_agisdk OK rate=%s close=%s bind=%s" % (r["rate"], r["close"], r["bind"]))
