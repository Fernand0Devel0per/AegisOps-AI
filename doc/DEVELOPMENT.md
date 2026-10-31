# Desenvolvimento local

A STORY-010 prepara o pacote e a cadeia de qualidade; ainda não há motor, API ou integração com LLM. As decisões e versões estão no [ADR-0003](adr/0003-ambiente-python-qualidade.md).

## Pré-requisitos

- Git, Python 3.14.8 padrão com GIL e uv 0.12.24 disponíveis no PATH. O arquivo `.python-version` indica a versão; se ela não estiver instalada, o uv pode provisioná-la.
- Internet para obter o interpretador, dependências e componentes de build na primeira instalação. Execuções posteriores sem rede dependem de os artefatos necessários já estarem no cache.
- Não são necessárias credenciais ou serviços pagos. Para validar contratos documentais separadamente, Python também precisa de PyYAML conforme [validação documental](standards/validation.md).

Na raiz de um clone, execute:

```sh
uv sync --locked --no-editable
uv run --locked --no-sync pytest -q
uv run --locked --no-sync ruff check src tests
uv run --locked --no-sync ruff format --check src tests
uv run --locked --no-sync mypy src tests
```

`uv.lock` fixa as dependências de desenvolvimento e seus artefatos; `--locked` rejeita lock desatualizado. O backend Hatchling e suas dependências de build têm versões fixadas em `pyproject.toml`, mas os hashes dos artefatos de build não são exigidos nesta configuração; essa é uma limitação da reprodução do build. A instalação não editável copia o pacote para o ambiente virtual `.venv`. O teste verifica que o pacote importado pertence ao ambiente ativo e que a distribuição está instalada, detectando instalação ausente ou importação acidental do código-fonte. Após alterar `src/`, execute novamente `uv sync --locked --no-editable` antes de testar, pois a instalação não é editável. O arquivo `.venv` é local e ignorado pelo Git.

O [workflow de qualidade](../.github/workflows/quality.yml) executa estes comandos no GitHub Actions. Sua presença não prova execução remota; os resultados realmente observados estão no handoff da atividade. Ações estão fixadas por hash de commit; atualizações devem trocar o hash por uma revisão verificada da ação e ser testadas junto com `uv` e o lockfile.

## Validação documental e cenários

```sh
python3 scripts/validate_repository.py
python3 scripts/validate_incidents.py
```

O primeiro comando usa PyYAML e funciona sem o plano original local ignorado pelo Git. Referências históricas a esse arquivo não são verificadas e seus links podem não abrir em clones; Q-014 acompanha a migração dessas referências. O segundo usa a biblioteca padrão e valida as fixtures sem implementar triagem. Detalhes estão no [guia de validação](standards/validation.md) e em [INCIDENTS](INCIDENTS.md).
