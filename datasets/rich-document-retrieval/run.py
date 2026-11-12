"""Controle de execução: C1 primeiro, depois ranking RICH-01; não lê julgamentos."""

import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import adapter
import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OLD = REPO / "datasets/rich-document-experiment"
CORPUS = REPO / "datasets/rich-documents"
OUT = ROOT / "output"
CPU = min(os.sched_getaffinity(0))
EXPECTED = {
    "manifest.yaml": "f9a0f97730c9fe7366c0dbcfc3843113565a43b0217ee41367b44e4ef3dd787a",
    "questions.yaml": "e21061f00d88453da2920c38232fd12c7a75e8eafe093f7b24618f43bae57fcd",
    "judgments.yaml": "7860c4e2eb8b84fffa3c9383da5735ae88bf5659d97ef211e3daa6899f5771ee",
}
FREEZE = {
    "extraction-freeze.json": "5d7dd517b0a7b45e79a1da3a6b2ae2d982cc96b8560cb3dd49e963a57cb72928",
    "chunk-freeze.json": "8aad19af2e30cd4ce11dbac0cf0081a62094ee4af395d245edab16bf748b6eb2",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def canonical(obj):
    return json.dumps(
        obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def verify_inputs():
    for file, expected in EXPECTED.items():
        if sha(CORPUS / file) != expected:
            raise ValueError("Hash do corpus divergente: " + file)
    manifest = yaml.safe_load((CORPUS / "manifest.yaml").read_text())
    for doc in manifest["documents"]:
        if sha(CORPUS / doc["file"]) != doc["sha256"]:
            raise ValueError("PDF divergente: " + doc["id"])
    for name, expected in FREEZE.items():
        path = OLD / "output" / name
        if sha(path) != expected:
            raise ValueError("Índice de hashes alterado: " + name)
        for pathref, value in json.loads(path.read_text())["files"].items():
            if sha(OLD / "output" / pathref) != value:
                raise ValueError("Saída histórica alterada: " + pathref)
    inventory = json.loads((OLD / "output/dependency-inventory.json").read_text())
    expected_supervisor = inventory["files_sha256"]["supervisor.py"]
    if sha(OLD / "supervisor.py") != expected_supervisor:
        raise ValueError("Supervisor histórico alterado")
    return manifest


def bubble(command, mounts):
    base = [
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
        "--dir",
        "/code",
        "--ro-bind",
        str(ROOT / "adapter.py"),
        "/code/adapter.py",
        "--ro-bind",
        str(ROOT / "ranker_worker.py"),
        "/code/ranker_worker.py",
        "--ro-bind",
        str(ROOT / "equivalence_worker.py"),
        "/code/equivalence_worker.py",
        "--ro-bind",
        str(OLD / "probe.py"),
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
        *mounts,
        "--remount-ro",
        "/",
        "--clearenv",
        "--setenv",
        "PATH",
        "/usr/bin",
        "--setenv",
        "PYTHONPATH",
        "/code:/pkg",
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
    return base + command


def execute(command, mounts):
    unit = "aegis063-" + uuid.uuid4().hex[:12]
    launch = [
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
        str(OLD / "supervisor.py"),
        *bubble(command, mounts),
    ]
    process = subprocess.run(
        launch, capture_output=True, text=True, timeout=45, check=False
    )
    if process.returncode:
        raise RuntimeError("Falha cgroup/supervisor: " + process.stderr[-1200:])
    result = json.loads(process.stdout)
    if result["status"] != "ok":
        raise RuntimeError("Processo interrompido: " + result.get("stderr", ""))
    result["result"] = json.loads(result.pop("stdout"))
    env = result["result"].get("sandbox", result["result"])
    network = env.get("network_namespace", env.get("namespace"))
    if network is not None and network == os.stat("/proc/self/ns/net").st_ino:
        raise RuntimeError("Rede não isolada")
    return result


def preflight():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        result = execute(
            ["/usr/bin/python3", "/code/probe.py", str(listener.getsockname()[1])], []
        )
    env = result["result"]
    if (
        env["host_loopback_access"]
        or [n for _, n in env["interfaces"]] != ["lo"]
        or env["temp_capacity_bytes"] != 104857600
        or env["writable_root"]
        or env["writable_dev"]
        or env["gabaritos_visible"]
        or len(env["cpu_affinity"]) != 1
    ):
        raise RuntimeError("Preflight insuficiente")
    dump(OUT / "preflight.json", result)


def temp_json(folder, name, value):
    path = Path(folder) / name
    dump(path, value)
    return path


def equivalence():
    verify_inputs()
    OUT.mkdir(exist_ok=True)
    preflight()
    with tempfile.TemporaryDirectory(prefix="aegis063-c1-") as tmp:
        root = Path(tmp)
        pkg = root / "aegisops"
        (pkg / "data/runbooks").mkdir(parents=True)
        for name in ("__init__.py", "retrieval.py"):
            shutil.copyfile(REPO / "src/aegisops" / name, pkg / name)
        for file in (REPO / "datasets/runbooks").glob("*.md"):
            shutil.copyfile(file, pkg / "data/runbooks" / file.name)
        queries = yaml.safe_load(
            (REPO / "datasets/evaluation/queries.yaml").read_text()
        )["queries"]
        path = temp_json(tmp, "c1queries.json", [q["text"] for q in queries])
        report = execute(
            ["/usr/bin/python3", "/code/equivalence_worker.py"],
            ["--ro-bind", str(root), "/pkg", "--ro-bind", str(path), "/c1queries.json"],
        )
    if report["result"]["status"] != "pass":
        raise RuntimeError("Equivalência não comprovada")
    report["protocol_sha256"] = sha(ROOT / "protocol.md")
    report["adapter_sha256"] = sha(ROOT / "adapter.py")
    report["equivalence_worker_sha256"] = sha(ROOT / "equivalence_worker.py")
    report["original_retrieval_sha256"] = sha(REPO / "src/aegisops/retrieval.py")
    dump(OUT / "equivalence-c1.json", report)
    print("PASS equivalência C1:", report["result"], flush=True)


def records_for(mode, manifest):
    records = []
    provenance = {}
    for doc in manifest["documents"]:
        file = OLD / "output/chunks" / mode / "fixed" / (doc["id"] + ".json")
        chunkfile = json.loads(file.read_text())
        total = 0
        for no, chunk in enumerate(chunkfile["chunks"], 1):
            ident = f"{doc['id']}-P{chunk['page']:02d}-C{no:03d}"
            text = chunk["text"]
            total += len(text.encode("utf-8"))
            records.append({"id": ident, "text": text})
            provenance[ident] = {
                "document_id": doc["id"],
                "document_version": doc["version"],
                "pdf_sha256": doc["sha256"],
                "page": chunk["page"],
                "start": chunk["start"],
                "end": chunk["end"],
                "section": None,
                "section_status": "not_extracted",
                "chunk_file": str(file.relative_to(REPO)),
                "chunk_file_sha256": sha(file),
            }
        if total > 1048576:
            raise ValueError("Limite de texto por documento excedido")
    if len(records) > 200 or len({r["id"] for r in records}) != len(records):
        raise ValueError("Unidades duplicadas ou limite excedido")
    return records, provenance


def timed_payload(payload):
    with tempfile.TemporaryDirectory(prefix="aegis063-payload-") as tmp:
        file = temp_json(tmp, "payload.json", payload)
        return execute(
            ["/usr/bin/python3", "/code/ranker_worker.py"],
            ["--ro-bind", str(file), "/payload.json"],
        )


def repeated(payload, tag, measurements):
    accepted = None
    for repeat in range(4):
        report = timed_payload(payload)
        result = report.pop("result")
        value = result["result"]
        report.update(tag)
        report.update(
            {
                "repeat": repeat,
                "phase": "warmup" if repeat == 0 else "measured",
                "operation_seconds": result["operation_seconds"],
                "sandbox": result["sandbox"],
            }
        )
        measurements.append(report)
        if accepted is None:
            accepted = value
        elif accepted != value:
            raise RuntimeError("Resultado não determinístico: " + str(tag))
    return accepted


def rank():
    manifest = verify_inputs()
    eq = json.loads((OUT / "equivalence-c1.json").read_text())
    if (
        eq["result"]["status"] != "pass"
        or eq["adapter_sha256"] != sha(ROOT / "adapter.py")
        or eq["equivalence_worker_sha256"] != sha(ROOT / "equivalence_worker.py")
        or eq["protocol_sha256"] != sha(ROOT / "protocol.md")
        or eq["original_retrieval_sha256"] != sha(REPO / "src/aegisops/retrieval.py")
    ):
        raise RuntimeError("Equivalência não válida para código atual")
    if (OUT / "ranking-freeze.json").exists():
        raise RuntimeError("Rankings já congelados; usar cópia isolada para reproduzir")
    preflight()
    questions = yaml.safe_load((CORPUS / "questions.yaml").read_text())["questions"]
    if len(questions) != 13:
        raise ValueError("Número de perguntas incorreto")
    rankings = []
    measurements = []
    provenance = {}
    indexes = {}
    for configuration, mode in [("B1", "poppler"), ("C1", "pdfplumber")]:
        records, refs = records_for(mode, manifest)
        provenance[configuration] = refs
        built = repeated(
            {
                "operation": "index",
                "records": records,
                "sha256": adapter.digest(records),
            },
            {"stage": "index", "configuration": configuration},
            measurements,
        )
        indexes[configuration] = {
            "index_size_bytes": built["index_size_bytes"],
            "chunks": built["chunks"],
            "unique_terms": built["unique_terms"],
            "term_occurrences": built["term_occurrences"],
            "records_sha256": adapter.digest(records),
            "index_sha256": hashlib.sha256(canonical(built["index"])).hexdigest(),
        }
        for query in questions:
            for k in (3, 5):
                result = repeated(
                    {
                        "operation": "query",
                        "index": built["index"],
                        "query": query["question"],
                        "k": k,
                    },
                    {
                        "stage": "query",
                        "configuration": configuration,
                        "question_id": query["id"],
                        "k": k,
                    },
                    measurements,
                )
                rankings.append(
                    {
                        "configuration": configuration,
                        "question_id": query["id"],
                        "k": k,
                        **result,
                    }
                )
                print("ranking", configuration, query["id"], "k", k, flush=True)
    dump(OUT / "provenance.json", provenance)
    dump(OUT / "index-statistics.json", indexes)
    dump(OUT / "measurements.json", measurements)
    dump(OUT / "rankings.json", rankings)
    dump(
        OUT / "environment.json",
        {
            "python": sys.version,
            "os": platform.platform(),
            "cpu": CPU,
            "protocol_sha256": sha(ROOT / "protocol.md"),
            "adapter_sha256": sha(ROOT / "adapter.py"),
            "worker_sha256": sha(ROOT / "ranker_worker.py"),
            "controller_sha256": sha(ROOT / "run.py"),
            "equivalence_sha256": sha(OUT / "equivalence-c1.json"),
            "corpus_hashes": EXPECTED,
            "frozen_062_hashes": FREEZE,
        },
    )
    files = [
        "rankings.json",
        "provenance.json",
        "index-statistics.json",
        "measurements.json",
        "environment.json",
    ]
    dump(
        OUT / "ranking-freeze.json",
        {
            "files": {name: sha(OUT / name) for name in files},
            "protocol_sha256": sha(ROOT / "protocol.md"),
            "note": "Congelado antes do avaliador consultar judgments.yaml ou semantic-review.yaml.",
        },
    )
    verify_inputs()
    print("PASS rankings congelados antes de carregar gabaritos", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("equivalence", "rank"):
        raise SystemExit("Uso: run.py equivalence|rank")
    {"equivalence": equivalence, "rank": rank}[sys.argv[1]]()
