# AegisOps AI

*Evidence-first Agentic Reliability Platform*

Plataforma de estudo e portfólio para investigar incidentes de serviços correlacionando sinais operacionais e documentação. A proposta é apoiar a triagem humana com observações, hipóteses, evidências verificáveis e limitações explícitas. Não há promessa de descoberta automática da causa raiz.

**Estado em 30/10/2026:** fundação documental preparada e proposta de produto aceita na STORY-001. Colibri e OLMoE foram testados localmente de forma exploratória; não há aplicação, API, testes de produto ou integração implementados.

## Problema e capacidades previstas

Investigar degradação exige reunir métricas, alertas, eventos e runbooks dispersos. O AegisOps pretende tornar esse processo rastreável, começando com dados sintéticos e ferramentas somente de consulta.

- Iniciar e consultar investigações por API; CLI é uma alternativa inicial a definir.
- Classificar severidade por regras determinísticas e indicar informações insuficientes.
- Recuperar runbooks Markdown com identificação de origem e versão.
- Produzir hipóteses e recomendações com referências verificadas por regras independentes do LLM.
- Funcionar localmente sem credenciais, com modo determinístico/mock.
- Evoluir com avaliação, observabilidade, durabilidade e controles de segurança demonstráveis.

Remediação automática, acesso a ambientes de terceiros e operação empresarial não fazem parte do MVP. Todos os itens acima estão **planejados**.

## Arquitetura prevista

```text
Usuário → API/CLI → workflow simples de investigação
                    ├─ triagem determinística ← sinais sintéticos
                    ├─ recuperação ← runbooks versionados
                    ├─ explicação ← LLM local, com fallback determinístico
                    └─ verificação de evidências → relatório para revisão humana
```

A primeira vertical será: **incidente sintético → severidade e evidências determinísticas + explicação por LLM local**, com fallback sem explicação. O ponto de partida aprovado é monolito modular; fronteiras internas serão desenhadas conforme as necessidades. Telemetria do AegisOps e dados do incidente investigado devem permanecer distinguíveis.

Consulte a [arquitetura e análise do plano](doc/architecture/overview.md), o [ADR-0001](doc/adr/0001-monolito-modular-baseline-deterministico.md) e o [ADR-0002](doc/adr/0002-llm-local-primeira-vertical.md).

## Stack identificada no plano

| Momento | Tecnologias candidatas ou direcionamento |
|---|---|
| Primeira implementação | Colibri e LLM local para explicação; Python, FastAPI, Pydantic e ferramentas de qualidade como candidatas |
| Após primeira vertical | Busca lexical em Markdown; análise ampliada; Docker/Compose após API inicial |
| Mediante avaliação | LangGraph; Docling; embeddings; FAISS/pgvector; PostgreSQL; workers e Redis/RabbitMQ |
| Evolução da plataforma | OpenTelemetry, Collector, Prometheus, Grafana; Kubernetes, Helm/Kustomize; Argo CD; HPA/KEDA condicionados a medições |
| Antes de conectores remotos reais | Autenticação/autorização, OIDC/JWT e permissões por ferramenta, a especificar |

O Colibri foi compilado e um modelo foi testado fora do repositório; não há dependências de aplicação instaladas no projeto. A tabela do plano contém escolhas preferenciais e candidatas; não significa adoção de todas as ferramentas. Versões, gerenciador e verificador de tipos ainda precisam de decisão registrada.

## Implementado e planejado

| Situação | Entrega |
|---|---|
| Preparado | Contrato dos agentes, templates YAML, catálogo de planejamento, ADR inicial, especificação/atividade de descoberta e handoff do bootstrap |
| Concluído | [STORY-001 — produto, usuário e limites](roadmap/stories/STORY-001.yaml); aceite da descoberta completa permanece pendente |
| Pendente na Etapa 0 | Três cenários sintéticos, requisitos observáveis e revisão de descoberta |
| Planejado | Ambiente Python, primeira API, motor de triagem e evolução por etapas |

Não há comando de inicialização ou teste da aplicação neste momento. O validador da documentação está disponível conforme as instruções abaixo. Não existem badges de CI, demo ou métricas de qualidade de produto.

## Roadmap

| Etapa | Entrega prevista |
|---|---|
| 0 | Descoberta, incidentes sintéticos e requisitos da vertical com núcleo determinístico e explicação local |
| 1 | Fundamentos Python, qualidade, CI e primeira API |
| 2 | Triagem determinística, explicação local avaliada e fallback para a candidata `v0.1.0` |
| 3–4 | Runbooks e busca lexical; depois análise ampliada com avaliação e validação |
| 5–6 | Avaliar orquestração explícita; RAG com documentos ricos e comparações medidas |
| 7–8 | Observabilidade e demo instrumentada; durabilidade e resiliência |
| 9–10 | Golden path de plataforma; avaliação de segurança e publicação demonstrável |

O [catálogo YAML](roadmap/index.yaml) é a fonte oficial de estados e dependências; o [guia do roadmap](roadmap/README.md) explica o refinamento. Histórias futuras precisam de especificação antes da execução. Não há issues remotas criadas.

## Organização

```text
.
├── AegisOps_AI_Plano_do_Zero.md   # fonte original preservada
├── AGENTS.md                    # entrada obrigatória dos agentes
├── roadmap/                     # índice, épicos, histórias e template
├── doc/
│   ├── architecture/            # visão e análise de viabilidade
│   ├── adr/                     # decisões arquiteturais e template
│   ├── decisions/               # pendências e reconciliação de instruções
│   └── standards/               # workflow, convenções e validação
├── agents/                      # atividades, specs, handoffs e templates
├── scripts/                     # validação dos contratos documentais
└── src/                         # reservado, sem implementação
```

`doc/` é o caminho canônico nesta execução, conforme o pedido de bootstrap. Os caminhos `docs/` mencionados no plano correspondem a `doc/`; veja o [registro de adaptações](doc/decisions/bootstrap-scope.md). Testes, datasets e deploy só receberão diretórios quando houver entregas que os utilizem.

## Contribuir com agentes

1. Leia [AGENTS.md](AGENTS.md), o [plano original](AegisOps_AI_Plano_do_Zero.md) e o [workflow](doc/standards/workflow.md).
2. Selecione uma história autorizada e confira dependências, critérios de aceite, ADRs e handoff anterior.
3. Prepare a especificação e a atividade antes de implementar. A primeira dupla já está em [SPEC-001](agents/specs/SPEC-001.yaml) e [ACT-001](agents/activities/ACT-001.yaml).
4. Valide os entregáveis, registre evidências, submeta à revisão e deixe um handoff com o estado real. Atualize a história e o índice em conjunto.

Para validar esta documentação, use Python 3 com PyYAML. Se precisar de ambiente isolado, os comandos estão no [guia de validação](doc/standards/validation.md):

```bash
python3 scripts/validate_repository.py
```

O histórico Git inicial foi removido por solicitação do proprietário. A pasta está sem repositório Git; uma nova inicialização e publicação permanecem pendentes. O plano original foi preservado localmente e incluído no `.gitignore`; suas referências e a dependência do validador precisam ser migradas para documentos públicos antes da publicação. A validação de documentos não substitui testes da futura aplicação.

## Decisões e limites

Decisões arquiteturais relevantes usam [ADRs](doc/adr/README.md). Questões de produto, riscos, escolhas técnicas pendentes e participação humana estão no [registro de pendências](doc/decisions/open-questions.md). O [handoff do bootstrap](agents/handoffs/HANDOFF-000.yaml) contém a evidência da entrega documental.

Não foi definida uma licença de distribuição. Essa decisão cabe ao proprietário antes da publicação; não há concessão de licença inferida por este README.
