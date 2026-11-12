#!/usr/bin/env python3
"""Structural checks only: semantic support and visual layout require review."""
from __future__ import annotations
import argparse
import copy
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parent
FAMILIES = {'texto_simples', 'tabela', 'duas_colunas', 'hierarquia', 'multiplas_paginas'}

def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)

def read(root: Path, name: str) -> dict:
    return yaml.safe_load((root / name).read_text(encoding='utf-8'))

def normalized(text: str) -> str:
    return ' '.join(text.split())

def output(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=10).stdout

def local_file(root: Path, relative: str, directory: str) -> Path:
    path = (root / relative).resolve()
    require(path.parent == (root / directory).resolve() and path.is_file(), f'Caminho inválido: {relative}')
    return path

def unique(items: list[dict], key: str) -> dict:
    result = {item[key]: item for item in items}
    require(len(result) == len(items), f'IDs duplicados: {key}')
    return result

def check(root: Path) -> None:
    manifest, questions, judgments = (read(root, name) for name in ('manifest.yaml','questions.yaml','judgments.yaml'))
    version = manifest['corpus_version']
    require(version == questions['corpus_version'] == judgments['corpus_version'], 'Versões do corpus divergentes')
    docs = unique(manifest['documents'], 'id')
    qs = unique(questions['questions'], 'id')
    js = unique(judgments['judgments'], 'question_id')
    require(len(docs) == 5 and {d['family'] for d in docs.values()} == FAMILIES, 'Cobertura de documentos inválida')
    require(12 <= len(qs) <= 15 and qs.keys() == js.keys(), 'Perguntas e julgamentos incompatíveis')
    require({d['file'] for d in docs.values()} == {f'documents/{p.name}' for p in (root/'documents').glob('*.pdf')}, 'Arquivos divergentes do manifesto')
    require({d['source'] for d in docs.values()} == {f'source/{p.name}' for p in (root/'source').glob('*.yaml')}, 'Fontes divergentes do manifesto')
    page_text = {}
    for ident, doc in docs.items():
        require(all(doc.get(k) for k in ('name','purpose','authorship','authorization','version','sha256','sections','scenario_groups')), f'{ident}: metadados ausentes')
        path = local_file(root, doc['file'], 'documents')
        source = local_file(root, doc['source'], 'source')
        source_data = yaml.safe_load(source.read_text(encoding='utf-8'))
        require(source_data['id'] == ident and source_data['family'] == doc['family'], f'{ident}: fonte divergente')
        require(path.stat().st_size <= 5 * 1024 * 1024, f'{ident}: tamanho excedido')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == doc['sha256'], f'{ident}: hash incorreto')
        info = output('pdfinfo', str(path))
        match = re.search(r'^Pages:\s+(\d+)$', info, re.MULTILINE)
        require(match is not None and int(match.group(1)) == doc['pages'] == len(source_data['pages']) and 1 <= doc['pages'] <= 10, f'{ident}: páginas incorretas')
        for page in range(1, doc['pages'] + 1):
            page_text[ident, page] = output('pdftotext','-layout','-f',str(page),'-l',str(page),str(path),'-')
        for section in doc['sections']:
            require(any(section in normalized(page_text[ident, p]) for p in range(1, doc['pages']+1)), f'{ident}: seção ausente: {section}')
    for ident, question in qs.items():
        judgment = js[ident]
        require(all(question.get(k) for k in ('question','intent','scenario_group')), f'{ident}: pergunta incompleta')
        require(judgment['corpus_version'] == version and judgment['human_review'] in ('pending','approved','rejected'), f'{ident}: versão/revisão inválida')
        require(judgment.get('justification') and judgment.get('relation'), f'{ident}: justificativa/relação ausente')
        evidence = judgment['evidence']
        if judgment['status'] == 'absent':
            require(not judgment['expected_answer'] and not evidence and version in judgment['relation'] and 'todas as páginas' in judgment['justification'], f'{ident}: ausência incompleta')
            continue
        require(judgment['status'] == 'answerable' and judgment['expected_answer'] and evidence, f'{ident}: resposta incompleta')
        for e in evidence:
            doc = docs[e['document_id']]
            require(e['document_version'] == doc['version'] and 1 <= e['page'] <= doc['pages'], f'{ident}: documento/página inválida')
            require(all(part in doc['sections'] for part in e['section'].split(' > ')), f'{ident}: seção inválida')
            page = page_text[e['document_id'],e['page']]
            require(all(part in normalized(page) for part in e['section'].split(' > ')), f'{ident}: seção não está na página')
            # Table anchors encode a row as cells separated by |; test same physical line.
            parts = e['anchor'].split(' | ')
            if len(parts) > 1:
                require(any(all(part in line for part in parts) for line in page.splitlines()), f'{ident}: linha da tabela ausente')
            else:
                require(normalized(e['anchor']) in normalized(page), f'{ident}: âncora ausente na página')
        for doc_id in {e['document_id'] for e in evidence}:
            require(ident in docs[doc_id]['question_ids'] and question['scenario_group'] in docs[doc_id]['scenario_groups'], f'{ident}: vínculo de grupo ausente')
        if 'table' in judgment:
            table = judgment['table']; page = page_text[evidence[0]['document_id'],evidence[0]['page']]
            require(all(table.get(k) and table[k] in page for k in ('header','row','column','unit')), f'{ident}: coordenadas da tabela inválidas')
    for doc_id, doc in docs.items():
        expected = {i for i, j in js.items() if any(e['document_id'] == doc_id for e in j['evidence'])}
        require(set(doc['question_ids']) == expected, f'{doc_id}: perguntas do manifesto divergentes')
        require(set(doc['scenario_groups']) == {qs[i]['scenario_group'] for i in expected}, f'{doc_id}: grupos divergentes')
    print(f'PASS: {len(docs)} PDFs, {len(page_text)} páginas, {len(qs)} perguntas; verificações estruturais, não semânticas.')

def self_test() -> None:
    mutations = ['hash','duplicate','page','anchor','group','absence','table','missing_file']
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / 'corpus'; shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('__pycache__'))
        check(root)
        for mutation in mutations:
            name = 'manifest.yaml' if mutation in ('hash','group') else 'questions.yaml' if mutation == 'duplicate' else 'judgments.yaml'
            data = read(root,name)
            if mutation == 'hash': data['documents'][0]['sha256'] = '0'*64
            elif mutation == 'duplicate': data['questions'].append(copy.deepcopy(data['questions'][0]))
            elif mutation == 'page': data['judgments'][0]['evidence'][0]['page'] = 999
            elif mutation == 'anchor': data['judgments'][0]['evidence'][0]['anchor'] = 'trecho inexistente'
            elif mutation == 'group': data['documents'][0]['scenario_groups'] = ['outro']
            elif mutation == 'absence': next(j for j in data['judgments'] if j['status']=='absent')['justification'] = ''
            elif mutation == 'table': next(j for j in data['judgments'] if j['question_id']=='Q04')['evidence'][0]['anchor'] = 'Vega | 75 mensagens | 15 minutos'
            else: (root/'documents'/'RD-01.pdf').unlink()
            original = (root/name).read_text(); (root/name).write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
            try:
                check(root)
            except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError):
                print(f'PASS: mutação {mutation} rejeitada')
            else:
                raise AssertionError(f'Mutação não rejeitada: {mutation}')
            finally:
                (root/name).write_text(original)
                if mutation == 'missing_file': shutil.copy(ROOT/'documents'/'RD-01.pdf',root/'documents'/'RD-01.pdf')

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument('--self-test',action='store_true'); args = parser.parse_args()
    if args.self_test: self_test()
    else: check(ROOT)

if __name__ == '__main__': main()
