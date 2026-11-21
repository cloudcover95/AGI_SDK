#!/usr/bin/env python3
"""Offline close-rule check for AGI_SDK (v3). Stdlib only, no network, no model pull.
Rate 0.05; close = sha256(prev || pack || text)[:16]. Ports touched: none (no quant ports).
Flags: mint=false socket=false layer_one=false fetch=false ue5_launch=false. Bind 127.0.0.1 only (no server here)."""
import hashlib, sys
RATE = 0.05
FLAGS = {"mint": False, "socket": False, "layer_one": False, "fetch": False, "ue5_launch": False}
HOST = "127.0.0.1"

def close(prev: bytes, pack: bytes, text: bytes) -> str:
    return hashlib.sha256(prev + pack + text).hexdigest()[:16]

def trit_pack(vals, rate=RATE):
    t = [(-1 if v < -rate else 1 if v > rate else 0) for v in vals]
    return bytes((x + 1) for x in t)

def chain(texts, vals):
    prev = b"\x00" * 8
    out = []
    for tx in texts:
        c = close(prev, trit_pack(vals), tx.encode())
        out.append(c)
        prev = c.encode()
    return out

def selftest():
    vals = [-0.2, -0.05, 0.0, 0.05, 0.06, 0.3]
    assert trit_pack(vals) == bytes([0, 1, 1, 1, 2, 2]), "rate 0.05 packing"
    a = chain(["a", "b", "c"], vals); b = chain(["a", "b", "c"], vals)
    assert a == b and len(set(a)) == 3 and all(len(x) == 16 for x in a), "close chain"
    assert chain(["a", "x", "c"], vals)[2] != a[2], "tamper detection"
    assert not any(FLAGS.values()) and HOST == "127.0.0.1"
    return a

if __name__ == "__main__":
    print("OK", selftest()); sys.exit(0)
