"""Validate the frozen corpus and proposed judgments without running retrieval."""
from __future__ import annotations

import copy
import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(manifest: dict, dataset: dict) -> None:
    def require(condition: bool, message: str) -> None:
        if not condition:
            raise ValueError(message)

    units = manifest['units']
    unit_ids = [u['id'] for u in units]
    require(len(unit_ids) == len(set(unit_ids)) and bool(unit_ids), 'IDs de unidades duplicados ou ausentes')
    paths = [u['path'] for u in units]
    require(len(paths) == len(set(paths)), 'Caminhos de unidades duplicados')
    for u in units:
        path, license_path = ROOT / u['path'], ROOT / u['license_path']
        require(path.is_file() and license_path.is_file(), 'Arquivo ou licença inexistente')
        require(digest(path.read_bytes()) == u['sha256'], 'Hash da unidade divergente')
        require(digest(license_path.read_bytes()) == u['license_sha256'], 'Hash da licença divergente')
        text = path.read_text(encoding='utf-8')
        require(all(str(x) in text for x in (u['id'], u['version'], u['source_url'], u['source_sha256'])), 'Proveniência incompleta')
        require(all(str(s) in text for s in u['sections']), 'Seção ausente na unidade')
        require('## Excerpt' in text and 'Modification:' in text and 'Attribution:' in text, 'Metadados incompletos')
    canonical = ''.join(f"{u['sha256']}  {u['path']}\n" for u in sorted(units, key=lambda u: u['path']))
    corpus_hash = digest(canonical.encode('utf-8'))
    require(manifest['corpus_sha256'] == corpus_hash == dataset['corpus_sha256'], 'Hash do corpus divergente')
    require(manifest['corpus_version'] == dataset['corpus_version'], 'Versão do corpus divergente')
    ids, groups = set(), {}
    for q in dataset['queries']:
        require(q['id'] not in ids, 'Consulta duplicada')
        ids.add(q['id'])
        require(q['language'] in ('pt-BR', 'en') and bool(q['text']), 'Idioma ou texto inválido')
        require(q['corpus_version'] == manifest['corpus_version'] and q['corpus_sha256'] == corpus_hash, 'Consulta de outra versão')
        if q['fixture'] is not None:
            require((ROOT / q['fixture']).is_file(), 'Fixture inexistente')
            groups.setdefault(q['incident_id'], set()).add(q['group'])
        relevant = [x['id'] for x in q['relevant']]
        negative = [x['id'] for x in q['negative']]
        unjudged = q['unjudged']
        combined = relevant + negative + unjudged
        require(len(combined) == len(set(combined)) and set(combined) == set(unit_ids), 'Julgamentos duplicados ou referências inválidas')
        require(all(x.get('rationale') for x in q['relevant'] + q['negative']), 'Julgamento sem justificativa')
        require(q['absence'] == (not relevant), 'Ausência incompatível com relevantes')
        require(not q['absence'] or not unjudged, 'Ausência exige julgamento de todas as unidades')
        require(q['review']['status'] == 'proposta_pendente_po', 'Revisão humana não registrada')
    require(all(len(g) == 1 for g in groups.values()), 'Variantes do incidente em grupos distintos')
    for a, b in [('Q01', 'Q02'), ('Q03', 'Q04'), ('Q05', 'Q07'), ('Q06', 'Q08'), ('Q09', 'Q10')]:
        pair = [q for q in dataset['queries'] if q['id'] in (a, b)]
        require(len(pair) == 2 and pair[0]['group'] == pair[1]['group'], 'Grupo de tradução inconsistente')
        require({q['language'] for q in pair} == {'pt-BR', 'en'}, 'Par de idiomas inconsistente')
        require(all(pair[0][k] == pair[1][k] for k in ('relevant', 'negative', 'unjudged', 'absence')), 'Rótulos de tradução divergentes')
    require(dataset['split'] == 'nao_atribuido', 'Partição não revisada')


def self_test(manifest: dict, dataset: dict) -> None:
    def rejected(change) -> None:
        candidate = copy.deepcopy(dataset)
        change(candidate)
        try:
            check(manifest, candidate)
        except (ValueError, KeyError):
            return
        raise AssertionError('Entrada inválida aceita')

    rejected(lambda d: d['queries'].append(copy.deepcopy(d['queries'][0])))
    rejected(lambda d: d['queries'][0]['negative'].append(copy.deepcopy(d['queries'][0]['relevant'][0])))
    rejected(lambda d: d['queries'][0]['unjudged'].append('ID-INEXISTENTE'))
    rejected(lambda d: d['queries'][8].update(absence=True, unjudged=[d['queries'][8]['negative'].pop()['id']]))
    rejected(lambda d: d['queries'][6].update(group='outro-grupo'))
    rejected(lambda d: d.update(corpus_sha256='0' * 64))
    rejected(lambda d: d['queries'][0].update(fixture='datasets/incidents/inexistente.json'))
    print('PASS: 7 mutações inválidas rejeitadas')


def main() -> None:
    manifest = yaml.safe_load((ROOT / 'datasets/runbooks/manifest.yaml').read_text())
    dataset = yaml.safe_load((ROOT / 'datasets/evaluation/queries.yaml').read_text())
    check(manifest, dataset)
    print(f"PASS: {len(manifest['units'])} unidades, {len(dataset['queries'])} consultas, hashes e grupos")
    if sys.argv[1:] == ['--self-test']:
        self_test(manifest, dataset)
    elif sys.argv[1:]:
        raise SystemExit('Uso: validate.py [--self-test]')


if __name__ == '__main__':
    main()
