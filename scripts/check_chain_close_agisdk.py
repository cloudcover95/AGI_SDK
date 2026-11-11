#!/usr/bin/env python3
"""Chained-close inference-slice check for AGI_SDK (JuniorCloud LLC, Inference Core lane).

Additive, standalone, stdlib-only. Trit-packs two weight blocks (rate 0.05),
picks a layer tier for each, and chains the close rule
sha256(prev || pack || text)[:16] across both blocks, verifying that
replaying the chain reproduces the same final close.
Layer pick: T0 n < 512*512, T1 n < 1024*1024, T2 native C when .so exists, else T1.
Safety flags stay False; host is 127.0.0.1. No bench, LUT, GGUF, model pull, or network.
Quant ports touched: Home, OSai, FieldCore, Flagstaff, JuniorLLM.
"""
import hashlib
import os
import sys

RATE = 0.05
HOST = "127.0.0.1"
FLAGS = {"mint": False, "socket": False, "layer_one": False, "fetch": False, "ue5_launch": False}
PORTS = ("Home", "OSai", "FieldCore", "Flagstaff", "JuniorLLM")
T0_MAX = 512 * 512
T1_MAX = 1024 * 1024


def trit_pack(weights, rate=RATE):
    trits = [0 if abs(w) <= rate else (1 if w > 0 else -1) for w in weights]
    out = bytearray()
    for i in range(0, len(trits), 5):
        v = 0
        for t in reversed(trits[i:i + 5]):
            v = v * 3 + (t + 1)
        out.append(v)
    return bytes(out), trits


def pick_layer(n, so_path=None):
    if n < T0_MAX:
        return "T0"
    if n < T1_MAX:
        return "T1"
    return "T2" if so_path and os.path.exists(so_path) else "T1"


def close(prev, pack, text):
    return hashlib.sha256(prev + pack + text.encode("utf-8")).hexdigest()[:16]


def chain(blocks):
    prev = b"\x00" * 16
    tiers = []
    for i, w in enumerate(blocks):
        pack, trits = trit_pack(w)
        tiers.append(pick_layer(len(trits)))  # pack first, then pick
        prev = close(prev, pack, "AGI_SDK chain %d" % i).encode("ascii")
    return prev.decode("ascii"), tiers


def main():
    blocks = [[0.3, -0.2, 0.01, -0.04, 0.9], [-0.7, 0.05, 0.06, 0.0, -0.051, 0.2]]
    c1, tiers = chain(blocks)
    c2, _ = chain(blocks)
    ok = c1 == c2 and len(c1) == 16
    ok &= tiers == ["T0", "T0"]
    ok &= trit_pack([0.05, -0.05, 0.0501, -0.0501])[1] == [0, 0, 1, -1]
    ok &= pick_layer(T1_MAX, "/nonexistent/kernel.so") == "T1"
    ok &= RATE == 0.05 and not any(FLAGS.values()) and HOST == "127.0.0.1"
    print("ports:", ", ".join(PORTS))
    print("close:", c1)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
