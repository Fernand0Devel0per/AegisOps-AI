"""Worker isolado: entrada contém somente pares id/texto, configuração e consulta."""

import json
import os
import socket
import time

import adapter


def sandbox():
    env = {
        "network_namespace": os.stat("/proc/self/ns/net").st_ino,
        "interfaces": socket.if_nameindex(),
        "temp_capacity_bytes": sum(
            os.statvfs(p).f_blocks * os.statvfs(p).f_frsize
            for p in ("/tmp", "/dev/shm")
        ),
        "affinity": sorted(os.sched_getaffinity(0)),
    }
    if (
        [name for _, name in env["interfaces"]] != ["lo"]
        or env["temp_capacity_bytes"] > 104857600
        or len(env["affinity"]) != 1
    ):
        raise RuntimeError("Isolamento não comprovado")
    return env


def main():
    env = sandbox()
    with open("/payload.json", encoding="utf-8") as stream:
        payload = json.load(stream)
    started = time.monotonic()
    if payload["operation"] == "index":
        index = adapter.build(payload["records"], payload["sha256"])
        encoded = json.dumps(
            index, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        value = {
            "index": index,
            "index_size_bytes": len(encoded),
            "chunks": len(index),
            "unique_terms": len({t for x in index for t in x["terms"]}),
            "term_occurrences": sum(len(x["terms"]) for x in index),
        }
    elif payload["operation"] == "query":
        ranking = adapter.search(payload["index"], payload["query"], payload["k"])
        value = {
            "state": ranking["state"],
            "hits": ranking["hits"],
            "context": adapter.apply_budget(ranking["hits"], 1800),
        }
    else:
        raise ValueError("Operação desconhecida")
    elapsed = time.monotonic() - started
    print(
        json.dumps(
            {"result": value, "operation_seconds": elapsed, "sandbox": env},
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
