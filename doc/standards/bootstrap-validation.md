# Evidências de validação do bootstrap

Data: 2026-10-30. Escopo: STORY-000 / SPEC-000 / ACT-000. A preparação documental é distinta da descoberta e da implementação de produto.

## Execução

| Verificação executada | Resultado |
|---|---|
| `python3 scripts/validate_repository.py` | PASS: 43 YAML, 11 épicos, 22 histórias e 15 Markdown; templates, campos, estados, catálogo, dependências, vínculos, mapeamentos de ACs, evidências, links locais e hash do plano |
| `python3 scripts/validate_repository.py --self-test` | PASS: quatro entradas inválidas rejeitadas (chave duplicada, ciclo, índice divergente, AC sem mapeamento) e uma válida aceita |
| `ast.parse` do script, por Python | PASS: sintaxe Python válida |
| SHA-256 do plano, por `hashlib.sha256` | PASS: `9a22c8fff517e28556e7b32cb1bd35ffe5b7306f48ad90f1f74644d22c5cc078`, igual ao valor obtido antes de qualquer alteração |
| Asserções de estrutura e escopo, por Python | PASS: `src/` contém apenas `.gitkeep`; não há `pyproject.toml`, `doc/PRODUCT.md` ou `doc/REQUIREMENTS.md`; ACT-001 permanece `pending` |
| `git diff --cached --check -- . ':(exclude)AegisOps_AI_Plano_do_Zero.md'` | PASS: nenhuma falha de whitespace nos arquivos criados |
| `git remote -v` | Saída vazia: nenhum remoto configurado |

O plano original já contém espaços finais usados em Markdown. Ele foi excluído somente da checagem de whitespace da adição inicial para preservar seus bytes; a integridade do arquivo inteiro foi conferida por hash. A checagem com `--cached` inspeciona também os arquivos novos preparados para o primeiro commit.

O ambiente já disponibilizava Python 3, PyYAML 6.0.2 e Git 2.56.0. Não houve instalação de dependências. Não foram usados serviços externos, agentes delegados ou ferramentas de publicação.

## Revisão por critério de aceite

Autorrevisão documental pelo agente executor; não é validação humana ou revisão por um segundo agente.

| Critério de STORY-000 | Evidência e conclusão |
|---|---|
| AC-01 — preservar plano | Hash anterior e posterior idêntico; fonte original permanece na raiz |
| AC-02 — documentação e templates | README, AGENTS, workflow e cinco templates criados com campos solicitados; YAML validado |
| AC-03 — planejamento e próxima execução | EPIC-000–010 e 22 histórias; STORY-001 `ready`, SPEC-001 `ready`, ACT-001 `pending`; ADR-0001 aceito por fonte explícita; candidatas mantidas como pendências |
| AC-04 — consistência e evidências | Validador, self-test, asserções e whitespace passaram; HANDOFF-000 lista arquivos, motivos, resultados e próximo passo |

Foram comparadas a arquitetura alvo, a stack candidata, as Etapas 0–10, os cenários de avaliação e os limites de segurança com o plano lido integralmente. As adaptações de modo de colaboração e diretório estão em [bootstrap-scope.md](../decisions/bootstrap-scope.md). A documentação não declara capacidades de aplicação prontas. O gate humano da descoberta permanece pendente na STORY-004.

## Git

Repositório local inicializado na branch `main`; os 61 arquivos, incluindo o plano preservado, integram o commit inicial do bootstrap. O hash do commit deve ser consultado em `git log -1`, evitando incluir no próprio conteúdo um hash que dependeria dele. Nenhum remoto ou push integra esta entrega.

## Limites

Não há aplicação ou suíte de testes de produto; não foram executados testes de API, integração, carga, LLM ou deploy. CI remota, publicação, licença e aceite humano de produto não foram realizados. O bootstrap não encerra a Etapa 0.
