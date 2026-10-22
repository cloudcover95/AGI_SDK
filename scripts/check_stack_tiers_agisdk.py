#!/usr/bin/env python3
"""Inference-slice self-check for AGI_SDK (JuniorCloud LLC, additive).

Stdlib only. Checks the layer-stack tier pick (T0/T1/T2), the trit-pack
rate and close rule, and the LLC guard flags. No network, no model pull,
no GGUF, no bench, no LUT. Not a quant file; ports touched: none.
"""
import hashlib
import os
import sys

RATE = 0.05
GUARDS = {"mint": False, "socket": False, "layer_one": False,
          "fetch": False, "ue5_launch": False}
BIND_HOST = "127.0.0.1"
T0_MAX = 512 * 512
T1_MAX = 1024 * 1024


def pick_tier(n, so_path=None):
    """T0 Python trit for n < 512*512, T1 bit-plane numpy for n < 1024*1024,
    T2 native C when the .so exists, falling back to T1."""
    if n < T0_MAX:
        return "T0"
    if n < T1_MAX:
        return "T1"
    if so_path and os.path.exists(so_path):
        return "T2"
    return "T1"


def trit_pack(weights):
    """Ternarize to {-1,0,1} by a mean-abs threshold, pack 4 trits/byte."""
    if not weights:
        return b""
    scale = sum(abs(w) for w in weights) / len(weights) or 1.0
    trits = [0 if abs(w) < 0.5 * scale else (1 if w > 0 else -1) for w in weights]
    out = bytearray()
    for i in range(0, len(trits), 4):
        b = 0
        for j, t in enumerate(trits[i:i + 4]):
            b |= (t + 1) << (2 * j)
        out.append(b)
    return bytes(out)


def close(prev, pack, text):
    """Close rule: sha256(prev || pack || text)[:16]."""
    return hashlib.sha256(prev + pack + text.encode()).hexdigest()[:16]


def main():
    fails = []
    cases = [(0, "T0"), (T0_MAX - 1, "T0"), (T0_MAX, "T1"),
             (T1_MAX - 1, "T1"), (T1_MAX, "T1")]
    for n, want in cases:
        got = pick_tier(n, so_path="/nonexistent/libtrit.so")
        if got != want:
            fails.append("tier n=%d got %s want %s" % (n, got, want))
    if pick_tier(T1_MAX, so_path=__file__) != "T2":
        fails.append("tier T2 not picked when .so exists")
    pack = trit_pack([0.9, -0.8, 0.01, 0.4, -0.02, 1.2])
    if len(pack) != 2:
        fails.append("pack length")
    c1 = close(b"\x00" * 16, pack, "AGI_SDK")
    c2 = close(b"\x00" * 16, pack, "AGI_SDK")
    if c1 != c2 or len(c1) != 16:
        fails.append("close rule not deterministic/16 hex")
    if RATE != 0.05:
        fails.append("rate")
    if any(GUARDS.values()):
        fails.append("guard flag true")
    if BIND_HOST != "127.0.0.1":
        fails.append("bind host")
    if fails:
        print("FAIL: " + "; ".join(fails))
        return 1
    print("OK tiers=6 rate=%.2f close=%s guards=false bind=%s" % (RATE, c1, BIND_HOST))
    return 0


if __name__ == "__main__":
    sys.exit(main())
