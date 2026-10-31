# ADR-0003 — Ambiente Python e qualidade mínima

## Status

`accepted` pelo Product Owner (PO) em 2026-10-30, condicionado à aprovação no teste das ferramentas com Python 3.14; teste concluído com sucesso no mesmo dia. Não substitui ADR anterior. A implementação da STORY-010 depende da conclusão do gate da STORY-004.

## Contexto

A [STORY-010](../../roadmap/stories/STORY-010.yaml) exige instalação reproduzível, testes, lint, análise de tipos e CI, com justificativa de decisões estruturais antes de sua adoção. O plano prevê Python e sugere uv, pytest e Ruff, mas não fixa versões ou type checker. A primeira vertical mantém os limites dos [ADR-0001](0001-monolito-modular-baseline-deterministico.md) e [ADR-0002](0002-llm-local-primeira-vertical.md).

## Problema ou necessidade

Escolher um conjunto mínimo e reproduzível que funcione na máquina local e em CI, com teste de instalação de pacote e sem instalar ferramentas de runtime não necessárias para o setup.

## Alternativas consideradas

1. **Escolhida:** Python 3.14.8, uv, pytest, Ruff, mypy e Hatchling; registrar versões e lockfile, com CI repetindo os mesmos comandos. Inclui ferramentas dedicadas, mas oferece fluxo explícito para teste, lint, tipos e empacotamento.
2. **venv + pip + unittest + ferramentas separadas:** menos decisões sobre gerenciador, porém exige solução adicional para travar dependências transitivas e configurar lint e tipos reproduzíveis.
3. **Poetry com pytest e type checker:** também permite gerência de dependências, mas adiciona uma ferramenta diferente da já disponível localmente; não foi avaliada experimentalmente nesta atividade.

## Decisão

Usar, na STORY-010, Python **3.14.8**, `uv` **0.12.24**, `pytest` **9.2.0**, `ruff` **0.17.3**, `mypy` **2.4.1** e `hatchling` **1.33.0**. Fixar as versões diretas e registrar o lockfile `uv.lock` com transitivas. Usar um ambiente virtual local, empacotamento `src/` e GitHub Actions para executar instalação travada, testes, lint e tipos. Os testes de setup devem demonstrar que a instalação torna o pacote importável e que uma falha deliberada retorna código de erro. Não introduzir ainda FastAPI, LLM, banco ou dependências de negócio.

No código CI, fixar as versões das ações escolhidas e registrar como atualizá-las; não alegar execução remota sem evidência. O teste de falha controlada será local ou em CI quando disponível e seu resultado será identificado. A política exata de lint e tipos será proporcional ao primeiro pacote e documentada no contrato da STORY-010.

## Justificativa e evidências

Em 2026-10-30, a máquina já dispunha de Python 3.12.14, Python 3.14.8 e uv 0.12.24. Uma resolução temporária com `uv pip compile`, usando o interpretador local Python 3.12.14 e as quatro dependências exatas acima, retornou 15 pacotes resolvidos. Em seguida, um ambiente virtual temporário isolado instalou essas versões; `pytest --version`, `ruff --version`, `mypy --version` e a importação de Hatchling passaram. Após o PO recomendar Python 3.14, repetiu-se o teste com Python 3.14.8: resolução e instalação isoladas das versões propostas geraram 15 pacotes; um teste com pytest passou, Ruff e mypy passaram para o arquivo de prova e Hatchling foi importado. Comandos e resultados estão no [HANDOFF-004](../../agents/handoffs/HANDOFF-004.yaml). Isso não instalou dependências no projeto nem demonstrou funcionamento da aplicação, de instalação de clone limpo ou de CI. As páginas oficiais de [uv sobre lock e sync](https://docs.astral.sh/uv/concepts/projects/sync/), [pytest](https://pypi.org/project/pytest/), [Ruff](https://docs.astral.sh/ruff/) e [mypy](https://pypi.org/project/mypy/) descrevem as ferramentas; compatibilidade real ainda precisa ser comprovada por instalação limpa e testes. Python 3.14 foi escolhido por ser disponível localmente, mais recente e ter suporte previsto até outubro de 2030; não há afirmação de compatibilidade com todos os futuros provedores LLM. Será usado o interpretador padrão com GIL, sem adotar free-threading nesta decisão.

## Consequências positivas

- Um lockfile e comandos comuns podem facilitar reprodução local e em CI; isso será verificado, não é resultado já medido.
- Ruff cobre lint e formatação; pytest e mypy separam teste executável e análise de tipos.

## Consequências negativas e trade-offs

- `uv`, Hatchling, pytest, Ruff e mypy introduzem ferramentas e atualizações a manter; instalação inicial pode exigir internet.
- A versão fixada pode exigir provisionamento em outras máquinas; o lockfile não elimina diferenças de plataforma.
- GitHub Actions não comprova CI remota enquanto o repositório e a execução não estiverem disponíveis.

## Riscos

A resolução e o smoke test isolado não provam que a cadeia completa funcione no projeto nem garantem disponibilidade futura dos artefatos. Mitigar com instalação em clone limpo, testes de importação, execução local da cadeia e pinning validado; se falhar, investigar e registrar a falha antes de concluir o setup. Resolução e instalação exploratória foram feitas em diretórios temporários, sem registrar lockfile de produto nesta etapa.

## Referências

- [STORY-010](../../roadmap/stories/STORY-010.yaml), [questões abertas Q-004](../decisions/open-questions.md) e [gate de descoberta](../decisions/discovery-review.md).
- [Plano original local](../../AegisOps_AI_Plano_do_Zero.md), seções 5 e 6.
