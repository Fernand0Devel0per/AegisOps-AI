"""Avaliação exploratória congelada; executa o pacote instalado em processo isolado."""
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUERY_HASH = 'cfbb5f70cb669cacff739c4317c3fce7c5818386267dbe5f35d93888d2612f8b'
MANIFEST_HASH = '63fadc27c030b0647db84d63fa1fc7b93b31af069638af2560e7fdecffa34b30'


def validate_frozen() -> dict:
    import yaml

    query_path = ROOT / 'datasets/evaluation/queries.yaml'
    manifest_path = ROOT / 'datasets/runbooks/manifest.yaml'
    for path, expected in ((query_path, QUERY_HASH), (manifest_path, MANIFEST_HASH)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Arquivo congelado alterado: {path.name}')
    subprocess.run(['python3', str(ROOT / 'datasets/evaluation/validate.py')], check=True, capture_output=True)
    dataset = yaml.safe_load(query_path.read_text())
    if dataset['split'] != 'nao_atribuido':
        raise ValueError('Partição inesperada')
    return dataset


def recall_at(ids: list[str], relevant: set[str], k: int) -> float:
    return len(set(ids[:k]) & relevant) / len(relevant) if relevant else 0.0


def metric(rows: list[dict]) -> dict:
    positive = [r for r in rows if not r['absence'] and not r['error']]
    absent = [r for r in rows if r['absence'] and not r['error']]
    result = {'queries': len(rows), 'technical_failures': sum(bool(r['error']) for r in rows),
              'positive_denominator': len(positive), 'absence_denominator': len(absent),
              'unjudged_at_5': sum(r['unjudged'] for r in rows if not r['error']),
              'negative_at_5': sum(r['negative'] for r in rows if not r['error'])}
    for k in (3, 5):
        result[f'recall_sum_{k}'] = sum(r[f'recall_{k}'] for r in positive)
    result['reciprocal_rank_sum_5'] = sum(r['rr'] for r in positive)
    result['positive_abstentions'] = sum(not r['ids'] for r in positive)
    result['absence_returns'] = sum(bool(r['ids']) for r in absent)
    result['absence_abstentions'] = sum(not r['ids'] for r in absent)
    return result


def main() -> None:
    dataset = validate_frozen()
    queries = dataset['queries']
    code = '''import json, sys
from aegisops.retrieval import retrieve
for q in json.load(sys.stdin):
    try:
        r = retrieve(q)
        print(json.dumps({"ids": [p.id for p in r.passages], "error": None}))
    except Exception as e:
        print(json.dumps({"ids": [], "error": type(e).__name__}))
'''
    proc = subprocess.run([str(ROOT / '.venv/bin/python'), '-c', code], input=json.dumps([q['text'] for q in queries]),
                          text=True, capture_output=True, check=True, cwd='/tmp')
    outcomes = [json.loads(line) for line in proc.stdout.splitlines()]
    if len(outcomes) != len(queries):
        raise ValueError('Quantidade de respostas incompatível')
    rows = []
    for q, outcome in zip(queries, outcomes, strict=True):
        ids = outcome['ids']
        relevant = {item['id'] for item in q['relevant']}
        negatives = {item['id'] for item in q['negative']}
        positions = [i for i, value in enumerate(ids, 1) if value in relevant]
        rows.append({'id': q['id'], 'group': q['group'], 'language': q['language'], 'absence': q['absence'],
                     'ids': ids, 'error': outcome['error'], 'first': min(positions) if positions else None,
                     'rr': 1 / min(positions) if positions else 0,
                     'recall_3': recall_at(ids, relevant, 3),
                     'recall_5': recall_at(ids, relevant, 5),
                     'unjudged': len(set(ids) & set(q['unjudged'])), 'negative': len(set(ids) & negatives)})
    groups = {key: metric([r for r in rows if r['group'] == key]) for key in sorted({r['group'] for r in rows})}
    languages = {key: metric([r for r in rows if r['language'] == key]) for key in ('pt-BR', 'en')}
    print(json.dumps({'overall': metric(rows), 'languages': languages, 'groups': groups, 'queries': rows}, indent=2))


if __name__ == '__main__':
    main()
