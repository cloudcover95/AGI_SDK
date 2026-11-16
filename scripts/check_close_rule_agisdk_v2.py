#!/usr/bin/env python3
"""AGI_SDK close-rule self-check (additive, local only).

Rate 0.05; close rule sha256(prev || pack || text)[:16]. Touches ports: Home, OSai,
FieldCore, Flagstaff, JuniorLLM (named only, no sockets opened).
"""
import hashlib
import sys

RATE = 0.05
HOST = "127.0.0.1"
FLAGS = {"mint": False, "socket": False, "layer_one": False, "fetch": False, "ue5_launch": False}
PORTS = ["Home", "OSai", "FieldCore", "Flagstaff", "JuniorLLM"]


def close(prev: bytes, pack: bytes, text: bytes) -> str:
    return hashlib.sha256(prev + pack + text).hexdigest()[:16]


def main() -> int:
    a = close(b"", b"\x00\x01\x02", b"hello")
    b = close(b"", b"\x00\x01\x02", b"hello")
    c = close(b"x", b"\x00\x01\x02", b"hello")
    ok = (a == b and a != c and len(a) == 16 and RATE == 0.05
          and HOST == "127.0.0.1" and not any(FLAGS.values()))
    print(f"close={a} rate={RATE} host={HOST} ports={','.join(PORTS)} flags_false={not any(FLAGS.values())}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
