# Desenvolvimento local

A STORY-010 prepara o pacote e a cadeia de qualidade; a STORY-011 adiciona contratos locais de entrada. Ainda não há motor, API ou integração com LLM. As decisões e versões estão no [ADR-0003](adr/0003-ambiente-python-qualidade.md).

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

`uv.lock` fixa as dependências de desenvolvimento e seus artefatos; `--locked` rejeita lock desatualizado. O backend Hatchling e suas dependências de build têm versões fixadas em `pyproject.toml`, mas os hashes dos artefatos de build não são exigidos nesta configuração; essa é uma limitação da reprodução do build. A instalação não editável copia o pacote para o ambiente virtual `.venv`. O teste verifica que o pacote importado pertence ao ambiente ativo e que a distribuição está instalada, detectando instalação ausente ou importação acidental do código-fonte. Após alterar `src/`, force a reinstalação com `uv sync --locked --no-editable --reinstall-package aegisops-ai` antes de testar: a sincronização não editável simples pode manter uma cópia anterior do pacote. O arquivo `.venv` é local e ignorado pelo Git.

O [workflow de qualidade](../.github/workflows/quality.yml) executa estes comandos no GitHub Actions. Sua presença não prova execução remota; os resultados realmente observados estão no handoff da atividade. Ações estão fixadas por hash de commit; atualizações devem trocar o hash por uma revisão verificada da ação e ser testadas junto com `uv` e o lockfile.

## Validação documental e cenários

```sh
python3 scripts/validate_repository.py
python3 scripts/validate_incidents.py
```

O primeiro comando usa PyYAML e funciona sem o plano original local ignorado pelo Git. Referências históricas a esse arquivo não são verificadas e seus links podem não abrir em clones; Q-014 acompanha a migração dessas referências. O segundo usa a biblioteca padrão e valida as fixtures sem implementar triagem. Detalhes estão no [guia de validação](standards/validation.md) e em [INCIDENTS](INCIDENTS.md).

## Contratos de entrada locais

`aegisops.contracts.validate_incident` recebe um objeto Python já decodificado de JSON e devolve um `Incident` imutável com sinais, evidências e períodos, ou lança `InvalidIncident`. A exceção tem `state == "entrada_invalida"` e `errors` com caminhos e códigos estáveis, sem os valores recebidos; nenhum incidente parcial é devolvido. O chamador deve usar essa função como fronteira de validação: construir dataclasses diretamente não valida dados. A direção das rotas, dos erros HTTP e do framework foi aceita no [ADR-0004](adr/0004-api-local-contratos-http.md); implementação, versões e detalhes de transporte permanecem para a STORY-012.

```python
import json
from pathlib import Path
from aegisops.contracts import InvalidIncident, validate_incident

data = json.loads(Path("datasets/incidents/inc-001-latencia.json").read_text())
try:
    incident = validate_incident(data)
except InvalidIncident as exc:
    print(exc.state, [(error.path, error.code) for error in exc.errors])
else:
    print(incident.id, len(incident.signals))
```

O contrato aplica as métricas, unidades, intervalos UTC, períodos, domínios, tolerância absoluta de 0,000001 ponto percentual para 5xx e referências definidos em [requisitos](REQUIREMENTS.md). IDs são textos não vazios e únicos entre incidente, sinais e evidências dentro da entrada. Uma lista vazia de sinais e outra de evidências é aceita; a decisão futura de retornar `insuficiente` não é implementada aqui. Campos textuais de agregação, origem e resumo são exigidos, mas sua veracidade e semântica não são verificadas. Campos adicionais, inclusive `expected` e `limitations` das fixtures, são ignorados e não fazem parte do modelo. A referência resolvível não comprova causalidade nem o suporte semântico do resumo.

Depois do setup e com artefatos de build em cache, a reinstalação e os testes podem rodar sem rede:

```sh
uv sync --offline --locked --no-editable --reinstall-package aegisops-ai
uv run --offline --locked --no-sync pytest -q
uv run --offline --locked --no-sync ruff check src tests
uv run --offline --locked --no-sync ruff format --check src tests
uv run --offline --locked --no-sync mypy src tests
```
