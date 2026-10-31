#!/usr/bin/env python3
"""Verifica as fixtures documentais da STORY-002; não classifica incidentes."""
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIRECTORY = ROOT / 'datasets' / 'incidents'
CATEGORIES = {'latencia_elevada', 'alta_taxa_5xx', 'saturacao_recursos'}
METRICS = {'http_request_duration_p95': 'ms', 'http_5xx_rate': 'percent',
           'cpu_utilization': 'percent', 'memory_utilization': 'percent'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'chave JSON duplicada: {key}')
        result[key] = value
    return result


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f'{label}: texto obrigatório')


def identifier(value, prefix, seen):
    text(value, 'ID')
    require(value.startswith(prefix), f'ID {value}: prefixo inválido')
    require(value not in seen, f'ID duplicado: {value}')
    seen.add(value)


def period(value, label):
    require(isinstance(value, dict), f'{label}: período obrigatório')
    times = []
    for field in ('start', 'end'):
        stamp = value.get(field)
        text(stamp, f'{label}.{field}')
        require(stamp.endswith('Z'), f'{label}.{field}: exige UTC Z')
        times.append(datetime.fromisoformat(stamp[:-1] + '+00:00'))
    require(times[0] < times[1], f'{label}: início deve preceder fim')
    return times


def nonempty_list(value, label):
    require(isinstance(value, list) and len(value) > 0, f'{label}: lista não vazia obrigatória')
    return value


def validate(path, seen):
    case = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'valor inválido: {value}')))
    require(isinstance(case, dict), 'raiz deve ser objeto')
    identifier(case.get('id'), 'INC-', seen)
    require(case.get('synthetic') is True, 'synthetic deve ser true')
    for field in ('service', 'environment'):
        text(case.get(field), field)
    begin, end = period(case.get('window'), 'window')
    signal_ids = set()
    for signal in nonempty_list(case.get('signals'), 'signals'):
        require(isinstance(signal, dict), 'sinal deve ser objeto')
        identifier(signal.get('id'), 'SIG-', seen)
        signal_ids.add(signal['id'])
        metric = signal.get('metric')
        require(metric in METRICS and signal.get('unit') == METRICS[metric], f'{metric}: unidade inválida')
        for field in ('aggregation', 'source'):
            text(signal.get(field), f'sinal.{field}')
        value = signal.get('value')
        require(type(value) in (int, float) and math.isfinite(value) and value >= 0, f'{metric}: valor inválido')
        if signal['unit'] == 'percent':
            require(value <= 100, f'{metric}: percentual fora de 0 a 100')
        start, stop = period(signal.get('period'), signal['id'])
        require(begin <= start < stop <= end, f'{signal["id"]}: período fora da janela')
        if metric == 'http_5xx_rate':
            numerator, denominator = signal.get('numerator'), signal.get('denominator')
            require(type(numerator) is int and type(denominator) is int and 0 <= numerator <= denominator and denominator > 0,
                    f'{signal["id"]}: contagens inválidas')
            require(math.isclose(value, 100 * numerator / denominator, rel_tol=1e-9, abs_tol=1e-9),
                    f'{signal["id"]}: taxa incompatível com contagens')
    evidence_ids = set()
    for evidence in nonempty_list(case.get('evidence'), 'evidence'):
        require(isinstance(evidence, dict), 'evidência deve ser objeto')
        identifier(evidence.get('id'), 'EVD-', seen)
        evidence_ids.add(evidence['id'])
        require(evidence.get('signal_id') in signal_ids, f'{evidence["id"]}: sinal inexistente')
        text(evidence.get('summary'), 'evidence.summary')
    expected = case.get('expected')
    require(isinstance(expected, dict), 'expected deve ser objeto')
    require(expected.get('category') in CATEGORIES, 'categoria inválida')
    for field in ('severity', 'status'):
        text(expected.get(field), f'expected.{field}')
    cited = nonempty_list(expected.get('evidence_ids'), 'expected.evidence_ids')
    require(all(isinstance(item, str) for item in cited), 'IDs citados devem ser texto')
    require(len(cited) == len(set(cited)) and set(cited) <= evidence_ids, 'referências esperadas inválidas ou duplicadas')
    used = set()
    for reason in nonempty_list(expected.get('justifications'), 'expected.justifications'):
        require(isinstance(reason, dict), 'justificativa deve ser objeto')
        text(reason.get('text'), 'justificativa.text')
        refs = nonempty_list(reason.get('evidence_ids'), 'justificativa.evidence_ids')
        require(all(isinstance(item, str) for item in refs), 'IDs da justificativa devem ser texto')
        require(len(refs) == len(set(refs)) and set(refs) <= set(cited), 'referência de justificativa inválida ou duplicada')
        used.update(refs)
    require(used == set(cited) == evidence_ids, 'toda evidência deve constar em expected e em justificativa')
    require({e['signal_id'] for e in case['evidence']} == signal_ids, 'todo sinal deve ter evidência')
    limits = case.get('limitations')
    require(isinstance(limits, dict), 'limitations deve ser objeto')
    for field in ('observable', 'cannot_conclude'):
        for item in nonempty_list(limits.get(field), f'limitations.{field}'):
            text(item, f'limitations.{field}')
    return expected['category']


def main():
    paths = sorted(DIRECTORY.glob('*.json'))
    require(len(paths) == 3, f'esperados três arquivos JSON; encontrados {len(paths)}')
    seen = set()
    categories = [validate(path, seen) for path in paths]
    require(set(categories) == CATEGORIES and len(set(categories)) == 3, 'categorias ausentes ou repetidas')
    print(f'PASS: {len(paths)} fixtures; categorias distintas, {len(seen)} IDs únicos e referências válidas.')
    for path in paths:
        print(f'PASS: {path.relative_to(ROOT)}')
    print('NOTA: justificativas e limites exigem revisão semântica humana; nenhuma regra de severidade foi testada.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
