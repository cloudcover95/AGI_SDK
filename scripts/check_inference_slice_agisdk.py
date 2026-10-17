#!/usr/bin/env python3
"""AGI_SDK inference-slice self-check (JuniorCloud LLC, Inference Core lane).

Stdlib only. Encodes the layer stack pick and the shared trit-pack contract so
engines can confirm they agree on the rate and the close rule.

Layer stack (see JuniorLLM junior_osai/kernels/stack.py, JuniorHome docs/LAYER_STACK.md):
  T0 Python trit       for n < 512*512
  T1 bit-plane numpy   for n < 1024*1024
  T2 native C          when the .so exists, otherwise fall back to T1
Weights are trit-packed before the layer pick
(BitNet-mlx src/bitnet_mlx/core/trit_pack_front.py). No bench, no LUT, no GGUF.

Not a quant file; touches no ports.
"""
import hashlib
import os

BIND_HOST = "127.0.0.1"
TRIT_RATE = 0.05
FLAGS = {"mint": False, "socket": False, "layer_one": False,
         "fetch": False, "ue5_launch": False}

T0_MAX = 512 * 512
T1_MAX = 1024 * 1024


def trit_pack(weights, rate=TRIT_RATE):
    """Quantize floats to {-1, 0, 1} with a dead zone of `rate`, 5 trits/byte."""
    trits = [0 if abs(w) <= rate else (1 if w > 0 else -1) for w in weights]
    out = bytearray()
    for i in range(0, len(trits), 5):
        v = 0
        for t in reversed(trits[i:i + 5]):
            v = v * 3 + (t + 1)
        out.append(v)
    return bytes(out), trits


def close_rule(prev: bytes, pack: bytes, text: str) -> str:
    """sha256(prev || pack || text)[:16]"""
    return hashlib.sha256(prev + pack + text.encode("utf-8")).hexdigest()[:16]


def pick_layer(n: int, so_path=None) -> str:
    if n < T0_MAX:
        return "T0"
    if n < T1_MAX:
        return "T1"
    if so_path and os.path.exists(so_path):
        return "T2"
    return "T1"


def self_check() -> int:
    assert BIND_HOST == "127.0.0.1"
    assert all(v is False for v in FLAGS.values())
    pack, trits = trit_pack([0.9, -0.3, 0.01, -0.04, 0.2, -1.0, 0.0])
    assert trits == [1, -1, 0, 0, 1, -1, 0]
    assert len(pack) == 2
    c1 = close_rule(b"", pack, "slice")
    assert len(c1) == 16 and c1 == close_rule(b"", pack, "slice")
    assert close_rule(c1.encode(), pack, "slice") != c1
    assert pick_layer(10) == "T0"
    assert pick_layer(T0_MAX) == "T1"
    assert pick_layer(T1_MAX) == "T1"
    assert pick_layer(T1_MAX, "/nonexistent/stack.so") == "T1"
    print(f"ok rate={TRIT_RATE} close={c1} bind={BIND_HOST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_check())
