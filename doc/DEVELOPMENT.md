# Desenvolvimento local

A STORY-010 prepara o pacote e a cadeia de qualidade; a STORY-011 adiciona contratos locais de entrada. A STORY-012 concluiu a consulta HTTP local e saúde; a STORY-020 concluiu o núcleo de triagem, sem integração à API ou ao LLM. As decisões e versões estão no [ADR-0003](adr/0003-ambiente-python-qualidade.md).

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
uv run --locked --no-sync pyright
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

`aegisops.contracts.validate_incident` recebe um objeto Python já decodificado de JSON e devolve um `Incident` imutável com sinais, evidências e períodos, ou lança `InvalidIncident`. A exceção tem `state == "entrada_invalida"` e `errors` com caminhos e códigos estáveis, sem os valores recebidos; nenhum incidente parcial é devolvido. O chamador deve usar essa função como fronteira de validação: construir dataclasses diretamente não valida dados. A direção das rotas, dos erros HTTP e do framework foi aceita no [ADR-0004](adr/0004-api-local-contratos-http.md).

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

O contrato aplica as métricas, unidades, intervalos UTC, períodos, domínios, tolerância absoluta de 0,000001 ponto percentual para 5xx e referências definidos em [requisitos](REQUIREMENTS.md). IDs são textos não vazios e únicos entre incidente, sinais e evidências dentro da entrada. Uma lista vazia de sinais e outra de evidências é aceita; o núcleo de triagem retorna `insuficiente` para essa entrada. Campos textuais de agregação, origem e resumo são exigidos, mas sua veracidade e semântica não são verificadas. Campos adicionais, inclusive `expected` e `limitations` das fixtures, são ignorados e não fazem parte do modelo. A referência resolvível não comprova causalidade nem o suporte semântico do resumo.

Depois do setup e com artefatos de build em cache, a reinstalação e os testes podem rodar sem rede:

```sh
uv sync --offline --locked --no-editable --reinstall-package aegisops-ai
uv run --offline --locked --no-sync pytest -q
uv run --offline --locked --no-sync ruff check src tests
uv run --offline --locked --no-sync ruff format --check src tests
uv run --offline --locked --no-sync mypy src tests
uv run --offline --locked --no-sync pyright
```

## Núcleo local de triagem

`aegisops.triage.triage_incident(data)` recebe o objeto Python decodificado e chama `validate_incident` antes de classificar. Não aceite dataclasses construídas manualmente como dados validados: a interface recebe o objeto de entrada e rejeita instâncias em desacordo com o contrato. `InvalidIncident` é propagada com `state` e `errors` originais, sem resultado parcial nem valores recebidos.

```python
import json
from pathlib import Path
from aegisops.triage import triage_incident

data = json.loads(Path("datasets/incidents/inc-001-latencia.json").read_text())
result = triage_incident(data)
print(result.state, result.severity)  # classificado media
for item in result.observations:
    print(item.signal_id, item.value, item.unit, item.level, item.evidence_id)
print(result.limitations)
```

O resultado imutável contém `incident_id`, `state`, `severity`, `observations`, `limitations` e `explanation_state`. Cada observação contém o sinal, métrica, valor, unidade, período, nível e a evidência associada com menor ID lexicográfico; a ordem segue os sinais da entrada. A severidade é o máximo dos níveis, sem combinar períodos nem calcular médias de percentis. Os limiares e unidades são os exemplos sintéticos de [requisitos](REQUIREMENTS.md), não política operacional.

Sem sinais e evidências, o resultado é `insuficiente`, sem severidade e com limitação explícita. Para uma entrada classificável, cada métrica ausente aparece nas limitações; classificação parcial não demonstra ausência de degradação. `explanation_state` é `nao_solicitada`: frases canônicas, verificação e explicação com LLM pertencem à STORY-021. Observações não são hipóteses, não estabelecem causalidade nem recomendam remediação; uma referência válida não prova a veracidade do dado ou do resumo. Este núcleo não está conectado à API.

## Depreciação de tipos de geradores assíncronos

Funções decoradas com `@asynccontextmanager` devem anotar o retorno como `collections.abc.AsyncGenerator[T, None]`. A anotação `AsyncIterator[T]` nesse decorador é deprecada nas definições de tipos atuais. O Pyright 1.1.414 verifica `src/`, `tests/` e `scripts/` com `reportDeprecated = "error"`; o comando acima falha com código não zero quando encontra uma ocorrência. Ele complementa o mypy 2.4.1, que continua obrigatório: o typeshed incluído nessa versão não contém a sobrecarga deprecada e não detectou o caso mesmo com `deprecated` habilitado. Os testes em `tests/test_typecheck.py` exercitam exemplos temporários inválido e válido usando a configuração do projeto. A anotação explícita de `lifespan` usa uma exceção pontual de Ruff UP043, regra de concisão que prefere omitir o `None` padrão; `reportDeprecated` permanece ativo como erro e não é suprimido.

O extra `pyright[nodejs]` instala Node.js através de `nodejs-wheel-binaries`, travado no `uv.lock` para evitar download durante a verificação após o setup. A instalação inicial requer obter esse binário, de tamanho relevante. Plataformas sem wheel compatível podem exigir preparação diferente. O Pyright pode emitir um aviso para `yaml` em `scripts/validate_repository.py`, pois PyYAML é dependência separada da validação documental; isso não altera a regra de deprecação. O controle depende das definições de tipos empacotadas pela ferramenta e não cobre arquivos fora dos diretórios configurados nem código ignorado pelo analisador; exceções explícitas podem contorná-lo e devem ser revistas. Ver [ADR-0005](adr/0005-verificacao-deprecacao-tipos.md) e [HANDOFF-012](../agents/handoffs/HANDOFF-012.yaml).

## API local de consulta

Após a instalação, inicie em um terminal e mantenha o processo em execução:

```sh
uv run --offline --locked --no-sync uvicorn aegisops.api:app --host 127.0.0.1 --port 18765 --no-access-log
```

Em outro terminal, consulte os dados sintéticos ou exercite os erros:

```sh
curl -i http://127.0.0.1:18765/health
curl -i http://127.0.0.1:18765/v1/incidents/INC-001
curl -i http://127.0.0.1:18765/v1/incidents/%20%20
curl -i http://127.0.0.1:18765/v1/incidents/ausente
```

`GET /health` retorna `200 {"status":"ok"}` somente após inicialização concluída. As três fixtures em `datasets/incidents/` são incluídas no wheel em `aegisops/data/incidents/` por Hatchling, sem uma segunda cópia versionada; alterações nas fontes exigem reconstrução e reinstalação. A inicialização carrega os três recursos fixos do pacote, rejeita JSON malformado ou chaves repetidas, valida cada incidente pelo núcleo e verifica IDs únicos no catálogo. Arquivo ausente, ilegível ou inválido impede o servidor de iniciar. O health indica prontidão para o catálogo em memória validado no início, não verifica arquivos continuamente.

`GET /v1/incidents/{id}` retorna o modelo de domínio validado: `id`, `service`, `environment`, `synthetic`, `window`, `signals` e `evidence`; datas são ISO 8601 em UTC e campos `expected` e `limitations` das fixtures não são devolvidos. Comparação de ID é exata e sensível a maiúsculas, sem normalização nem limite adicional ao contrato de domínio; codifique caracteres reservados para transmissão. O cliente ou servidor pode normalizar segmentos `.` e `..`, decodificar barras ou impor limites de tamanho de URI, portanto nem toda representação do ID é necessariamente transmissível por todas as ferramentas HTTP. O ID jamais é usado como caminho para abrir arquivos e não há parâmetro de caminho de catálogo.

Erros retornam `application/problem+json`, com `type`, `title`, `status`, `detail` e `code`: espaços ou ID vazio geram `400 entrada_invalida`, ID inexistente gera `404 incidente_nao_encontrado`, falhas internas geram `500 erro_interno`; outras rotas e métodos também usam erros estruturados. Valores de entrada e detalhes internos não são refletidos. O log de acesso está desativado no comando acima; erros internos registram apenas mensagem genérica. A API não aceita incidentes novos. Não há documentação interativa nem OpenAPI habilitada nesta etapa, evitando dependência de ativos externos. O servidor escuta apenas em loopback; escolha outra interface somente quando seu ambiente e sua política de acesso permitirem.

FastAPI 0.162.0 e Uvicorn 0.54.0 são dependências de runtime; HTTPX2 2.15.1 é usado somente nos testes de integração. Foram escolhidos após teste isolado com Python 3.14.8; as transitivas estão travadas em `uv.lock`, e resultados e limitações constam do [handoff](../agents/handoffs/HANDOFF-012.yaml). A [documentação do Starlette](https://starlette.dev/testclient/) indica HTTPX2 para TestClient; FastAPI e Uvicorn são descritos em suas páginas oficiais no [PyPI](https://pypi.org/project/fastapi/0.162.0/) e [PyPI](https://pypi.org/project/uvicorn/0.54.0/). O workflow executa toda a suíte, incluindo `tests/integration`; execução remota desta alteração depende de publicação autorizada e não é presumida.
