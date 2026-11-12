#!/usr/bin/env python3
"""Runs inside a fresh systemd scope and records aggregate cgroup measurements."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def stat(path):
    return {
        line.split()[0]: int(line.split()[1])
        for line in path.read_text().splitlines()
        if len(line.split()) == 2
    }


def main():
    group = Path("/sys/fs/cgroup") / Path(
        Path("/proc/self/cgroup").read_text().strip().split("::")[1].lstrip("/")
    )
    memory = int((group / "memory.max").read_text())
    cpu = (group / "cpu.max").read_text().strip()
    if (
        memory > 1073741824
        or cpu != "100000 100000"
        or len(os.sched_getaffinity(0)) != 1
    ):
        raise RuntimeError("Limite cgroup/CPU não aplicado")
    before = stat(group / "cpu.stat")["usage_usec"]
    started = time.monotonic()
    try:
        done = subprocess.run(
            sys.argv[1:], capture_output=True, timeout=30, check=False
        )
        code = done.returncode
        out = done.stdout.decode("utf-8")
        err = done.stderr.decode("utf-8", errors="replace")[-4000:]
        status = "ok" if code == 0 else "failed"
        if len(done.stdout) > 8 * 1024 * 1024:
            status = "failed"
            err = "Saída serializada excedeu 8 MiB"
            out = ""
    except subprocess.TimeoutExpired:
        code = None
        out = ""
        err = "Prazo de 30 segundos excedido"
        status = "timeout"
    elapsed = time.monotonic() - started
    after = stat(group / "cpu.stat")["usage_usec"]
    print(
        json.dumps(
            {
                "status": status,
                "returncode": code,
                "stdout": out,
                "stderr": err,
                "wall_seconds": elapsed,
                "cpu_seconds": (after - before) / 1e6,
                "memory_peak_bytes": int((group / "memory.peak").read_text()),
                "memory_max_bytes": memory,
                "cpu_max": cpu,
                "affinity": sorted(os.sched_getaffinity(0)),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
