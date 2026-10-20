#!/usr/bin/env python3
"""Read loop.yaml (flat key: value with ${key} substitution).  `config.py KEY` prints one value.
Set LOOP_CONFIG=<file> to use another config (e.g. local clones for testing)."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path=None):
    path = path or os.environ.get("LOOP_CONFIG") or os.path.join(ROOT, "loop.yaml")
    cfg = {}
    for line in open(path):
        line = line.split("#", 1)[0].rstrip()
        if not line.strip() or ":" not in line:
            continue
        k, v = line.split(":", 1)
        cfg[k.strip()] = v.strip()
    for _ in range(3):
        for k, v in cfg.items():
            cfg[k] = re.sub(r"\$\{(\w+)\}", lambda m: cfg.get(m.group(1), ""), v)
    if not os.path.isabs(cfg.get("runs_dir", "runs")):
        cfg["runs_dir"] = os.path.join(ROOT, cfg.get("runs_dir", "runs"))
    return cfg


if __name__ == "__main__":
    c = load()
    print(c[sys.argv[1]] if len(sys.argv) > 1 else "\n".join(f"{k}={v}" for k, v in c.items()))
