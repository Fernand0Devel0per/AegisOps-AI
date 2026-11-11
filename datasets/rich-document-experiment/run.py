#!/usr/bin/env python3
"""Controlador local. Nenhum PDF é processado fora do sandbox."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import uuid
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CORPUS = REPO / "datasets/rich-documents"
DOCS = CORPUS / "documents"
OUTPUT = ROOT / "output"
SITE = Path.home() / ".local/lib/python3.14/site-packages"
EXPECTED = {
    "manifest.yaml": "f9a0f97730c9fe7366c0dbcfc3843113565a43b0217ee41367b44e4ef3dd787a",
    "questions.yaml": "e21061f00d88453da2920c38232fd12c7a75e8eafe093f7b24618f43bae57fcd",
    "judgments.yaml": "7860c4e2eb8b84fffa3c9383da5735ae88bf5659d97ef211e3daa6899f5771ee",
}
CPU = min(os.sched_getaffinity(0))


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    for name, expected in EXPECTED.items():
        if digest(CORPUS / name) != expected:
            raise RuntimeError("Hash divergente: " + name)
    manifest = yaml.safe_load((CORPUS / "manifest.yaml").read_text())
    for doc in manifest["documents"]:
        if digest(CORPUS / doc["file"]) != doc["sha256"]:
            raise RuntimeError("PDF alterado: " + doc["id"])
    return manifest


def bubble(command, extra):
    args = [
        "bwrap",
        "--ro-bind",
        "/usr",
        "/usr",
        "--ro-bind",
        "/etc",
        "/etc",
        "--ro-bind",
        "/lib",
        "/lib",
        "--ro-bind",
        "/lib64",
        "/lib64",
        "--ro-bind",
        str(SITE),
        "/deps",
        "--dir",
        "/code",
        "--ro-bind",
        str(ROOT / "worker.py"),
        "/code/worker.py",
        "--ro-bind",
        str(ROOT / "chunk_worker.py"),
        "/code/chunk_worker.py",
        "--ro-bind",
        str(ROOT / "probe.py"),
        "/code/probe.py",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--unshare-net",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--die-with-parent",
        "--size",
        "104853504",
        "--tmpfs",
        "/tmp",
        "--size",
        "4096",
        "--tmpfs",
        "/dev/shm",
        "--remount-ro",
        "/dev",
        *extra,
        "--remount-ro",
        "/",
        "--clearenv",
        "--setenv",
        "PATH",
        "/usr/bin",
        "--setenv",
        "PYTHONPATH",
        "/deps",
        "--setenv",
        "PYTHONDONTWRITEBYTECODE",
        "1",
        "--setenv",
        "HOME",
        "/tmp",
        "--chdir",
        "/tmp",
        "--",
    ]
    return args + command


def execute(command, extra):
    unit = "aegis062-" + uuid.uuid4().hex[:12]
    outer = [
        "systemd-run",
        "--user",
        "--scope",
        "--quiet",
        "--unit",
        unit,
        "-p",
        "MemoryMax=1073741824",
        "-p",
        "CPUQuota=100%",
        "-p",
        "TasksMax=32",
        "taskset",
        "-c",
        str(CPU),
        sys.executable,
        str(ROOT / "supervisor.py"),
        *bubble(command, extra),
    ]
    result = subprocess.run(
        outer, capture_output=True, text=True, timeout=45, check=False
    )
    if result.returncode:
        raise RuntimeError(
            f"Falha no escopo {result.returncode}: {result.stderr[-1000:]}"
        )
    value = json.loads(result.stdout)
    if value["status"] == "ok":
        value["result"] = json.loads(value.pop("stdout"))
        env = value["result"].get("sandbox", value["result"])
        if (
            env.get("namespace", env.get("network_namespace"))
            == os.stat("/proc/self/ns/net").st_ino
        ):
            raise RuntimeError("Namespace de rede não isolado")
    else:
        value.pop("stdout", None)
    return value


def preflight():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        report = execute(
            ["/usr/bin/python3", "/code/probe.py", str(port)],
            ["--ro-bind", str(DOCS), "/input"],
        )
    if report["status"] != "ok":
        raise RuntimeError("Falha de preflight: " + report["stderr"])
    p = report["result"]
    if (
        p["host_loopback_access"]
        or [x[1] for x in p["interfaces"]] != ["lo"]
        or p["temp_capacity_bytes"] != 104857600
        or p["writable_root"]
        or p["writable_dev"]
        or p["gabaritos_visible"]
        or len(p["cpu_affinity"]) != 1
    ):
        raise RuntimeError("Isolamento não satisfeito: " + str(p))
    dump(OUTPUT / "preflight.json", report)


def main():
    manifest = verify()
    OUTPUT.mkdir(exist_ok=True)
    preflight()
    packages = {
        n: metadata.version(n)
        for n in (
            "pdfplumber",
            "pdfminer.six",
            "Pillow",
            "pypdfium2",
            "charset-normalizer",
            "cryptography",
            "cffi",
            "pycparser",
            "ply",
        )
    }
    dump(
        OUTPUT / "environment.json",
        {
            "python": sys.version,
            "os": platform.platform(),
            "cpu": platform.processor(),
            "cpu_id": CPU,
            "pdfinfo_version": subprocess.run(
                ["pdfinfo", "-v"], capture_output=True, text=True, check=False
            ).stderr.splitlines()[0],
            "packages": packages,
            "protocol_sha256": digest(ROOT / "protocol.md"),
            "input_hashes": EXPECTED,
            "manifest": manifest,
        },
    )
    measurement = []
    for mode in ("poppler", "poppler_layout", "pdfplumber"):
        for doc in manifest["documents"]:
            accepted = None
            for repeat in range(4):
                entry = execute(
                    [
                        "/usr/bin/python3",
                        "/code/worker.py",
                        mode,
                        doc["id"],
                        str(doc["pages"]),
                    ],
                    ["--ro-bind", str(DOCS), "/input"],
                )
                result = entry.pop("result", None)
                entry.update(
                    {
                        "stage": "extract",
                        "configuration": mode,
                        "document_id": doc["id"],
                        "repeat": repeat,
                        "phase": "warmup" if repeat == 0 else "measured",
                    }
                )
                if result is not None:
                    # Timing and sandbox identities are measured metadata, not frozen semantic output.
                    entry["worker_timing"] = result.pop("timing_seconds")
                    entry["sandbox"] = result.pop("sandbox")
                    if accepted is None:
                        accepted = result
                    elif accepted != result:
                        entry["status"] = "nondeterministic"
                        entry["stderr"] = "Resultado diferente entre repetições"
                measurement.append(entry)
                if entry["status"] != "ok":
                    break
            if accepted is not None and all(
                x["status"] == "ok"
                for x in measurement
                if x["stage"] == "extract"
                and x["configuration"] == mode
                and x["document_id"] == doc["id"]
            ):
                dump(OUTPUT / "extractions" / mode / (doc["id"] + ".json"), accepted)
            print("extract", mode, doc["id"], measurement[-1]["status"], flush=True)
    dump(
        OUTPUT / "extraction-freeze.json",
        {
            "files": {
                str(p.relative_to(OUTPUT)): digest(p)
                for p in sorted((OUTPUT / "extractions").glob("*/*.json"))
            },
            "protocol_sha256": digest(ROOT / "protocol.md"),
        },
    )
    for mode in ("poppler", "pdfplumber"):
        for strategy in ("fixed", "structural"):
            if mode == "poppler" and strategy == "structural":
                measurement.append(
                    {
                        "stage": "chunk",
                        "configuration": mode + "/" + strategy,
                        "status": "infeasible",
                        "reason": "Poppler textual não fornece estrutura nativa.",
                    }
                )
                continue
            for doc in manifest["documents"]:
                path = OUTPUT / "extractions" / mode / (doc["id"] + ".json")
                if not path.exists():
                    measurement.append(
                        {
                            "stage": "chunk",
                            "configuration": mode + "/" + strategy,
                            "document_id": doc["id"],
                            "status": "not_processed",
                            "reason": "Extração falhou.",
                        }
                    )
                    continue
                accepted = None
                for repeat in range(4):
                    entry = execute(
                        ["/usr/bin/python3", "/code/chunk_worker.py", strategy],
                        ["--ro-bind", str(path), "/input.json"],
                    )
                    result = entry.pop("result", None)
                    entry.update(
                        {
                            "stage": "chunk",
                            "configuration": mode + "/" + strategy,
                            "document_id": doc["id"],
                            "repeat": repeat,
                            "phase": "warmup" if repeat == 0 else "measured",
                        }
                    )
                    if result is not None:
                        entry["worker_timing"] = result.pop("timing_seconds")
                        entry["sandbox"] = result.pop("sandbox")
                        if accepted is None:
                            accepted = result
                        elif accepted != result:
                            entry["status"] = "nondeterministic"
                            entry["stderr"] = "Resultado diferente entre repetições"
                    measurement.append(entry)
                    if entry["status"] != "ok":
                        break
                if accepted is not None and all(
                    x["status"] == "ok"
                    for x in measurement
                    if x["stage"] == "chunk"
                    and x["configuration"] == mode + "/" + strategy
                    and x.get("document_id") == doc["id"]
                ):
                    dump(
                        OUTPUT / "chunks" / mode / strategy / (doc["id"] + ".json"),
                        accepted,
                    )
                print(
                    "chunk",
                    mode,
                    strategy,
                    doc["id"],
                    measurement[-1]["status"],
                    flush=True,
                )
    dump(OUTPUT / "measurements.json", measurement)
    dump(
        OUTPUT / "chunk-freeze.json",
        {
            "files": {
                str(p.relative_to(OUTPUT)): digest(p)
                for p in sorted((OUTPUT / "chunks").glob("*/*/*.json"))
            }
        },
    )
    verify()


if __name__ == "__main__":
    main()
