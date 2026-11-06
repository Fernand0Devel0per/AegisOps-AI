"""Execute consultas usando o pacote instalado e devolva resultados em JSON por linha."""

import json
import sys

from aegisops.retrieval import retrieve


def retrieve_query(query: str) -> dict:
    try:
        result = retrieve(query)
    except Exception as error:  # noqa: BLE001 - falhas técnicas são registradas por consulta.
        return {"ids": [], "error": type(error).__name__}

    passage_ids = [passage.id for passage in result.passages]
    return {"ids": passage_ids, "error": None}


def main() -> None:
    queries = json.load(sys.stdin)
    for query in queries:
        outcome = retrieve_query(query)
        print(json.dumps(outcome))


if __name__ == "__main__":
    main()
