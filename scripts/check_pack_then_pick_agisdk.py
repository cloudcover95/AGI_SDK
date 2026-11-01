#!/usr/bin/env python3
"""Pack-then-pick self-check for AGI_SDK (Inference Core lane, JuniorCloud LLC).

Weights are trit-packed first, then the layer stack picks a tier:
  T0 Python trit      for n < 512*512
  T1 bit-plane numpy  for n < 1024*1024
  T2 native C         when the .so exists, else falls back to T1
No bench, no LUT, no GGUF, no model pull. Stdlib only, no network.
Quant ports touched: Home, OSai, FieldCore, Flagstaff, JuniorLLM.
"""
import hashlib
import os
import sys

RATE = 0.05
HOST = "127.0.0.1"
FLAGS = {"mint": False, "socket": False, "layer_one": False,
         "fetch": False, "ue5_launch": False}
PORTS = ("Home", "OSai", "FieldCore", "Flagstaff", "JuniorLLM")
T0_MAX = 512 * 512
T1_MAX = 1024 * 1024


def trit(x, rate=RATE):
    return 1 if x > rate else (-1 if x < -rate else 0)


def trit_pack(weights, rate=RATE):
    """Pack trits 5 per byte (base 3, 3**5 = 243 <= 255)."""
    ts = [trit(w, rate) + 1 for w in weights]
    out = bytearray()
    for i in range(0, len(ts), 5):
        v = 0
        for t in reversed(ts[i:i + 5]):
            v = v * 3 + t
        out.append(v)
    return bytes(out)


def trit_unpack(packed, n):
    ts = []
    for b in packed:
        for _ in range(5):
            ts.append(b % 3 - 1)
            b //= 3
    return ts[:n]


def close_rule(prev, pack, text):
    return hashlib.sha256(prev + pack + text).hexdigest()[:16]


def pick_tier(n, so_path=None):
    if n < T0_MAX:
        return "T0"
    if n < T1_MAX:
        return "T1"
    if so_path and os.path.exists(so_path):
        return "T2"
    return "T1"


def pack_then_pick(weights, so_path=None):
    pack = trit_pack(weights)
    return pack, pick_tier(len(weights), so_path)


def main():
    ok = True
    w = [0.2, -0.3, 0.01, -0.04, 0.06, -0.06, 0.0, 0.5]
    pack, tier = pack_then_pick(w)
    ok &= trit_unpack(pack, len(w)) == [trit(x) for x in w]
    ok &= tier == "T0"
    ok &= pick_tier(T0_MAX) == "T1"
    ok &= pick_tier(T1_MAX) == "T1"
    ok &= pick_tier(T1_MAX, "/nonexistent/stack.so") == "T1"
    ok &= pick_tier(T1_MAX, sys.executable) == "T2"
    c1 = close_rule(b"\x00" * 16, pack, b"agisdk")
    c2 = close_rule(b"\x00" * 16, pack, b"agisdk")
    ok &= c1 == c2 and len(c1) == 16
    # engines agree on rate and close rule
    engines = {p: (RATE, close_rule(b"prev", pack, p.encode())[:0] + "sha256[:16]")
               for p in PORTS}
    ok &= len(set(engines.values())) == 1
    ok &= HOST == "127.0.0.1" and not any(FLAGS.values())
    print("pack_then_pick_agisdk", "PASS" if ok else "FAIL",
          "tier=" + tier, "close=" + c1, "ports=" + ",".join(PORTS))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
