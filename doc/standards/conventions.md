# Convenções e rastreabilidade

## Arquivos e identificadores

UTF-8, finais de linha LF, Markdown para comunicação conceitual e YAML para contratos. YAML usa duas posições de indentação, chaves legíveis, listas simples, sem tags executáveis ou aliases. Datas são strings ISO `AAAA-MM-DD`; usar o contexto de data do usuário. Campos opcionais sem valor podem usar `null`; listas vazias são `[]`, não texto vazio.

| Tipo | ID | Arquivo |
|---|---|---|
| Épico | `EPIC-000` | `roadmap/epics/EPIC-000.yaml` |
| História | `STORY-001` | `roadmap/stories/STORY-001.yaml` |
| Especificação | `SPEC-001` | `agents/specs/SPEC-001.yaml` |
| Atividade | `ACT-001` | `agents/activities/ACT-001.yaml` |
| Handoff | `HANDOFF-001` | `agents/handoffs/HANDOFF-001.yaml` |
| ADR | `ADR-0001` | `doc/adr/0001-descricao-curta.md` |

Usar no mínimo três dígitos nos contratos e quatro nos ADRs. Os zeros de templates são exemplos; arquivos em `templates/` e `0000-template.md` não são entidades de catálogo. Os contratos reais `STORY/SPEC/ACT/HANDOFF-000` são o registro legítimo do bootstrap. O número do épico acompanha a etapa do plano. Os intervalos de histórias (001–004, 010–012, 020–021…) auxiliam leitura; não há obrigação de preencher lacunas.

Novos IDs são alocados verificando o índice e a pasta, sem reutilizar um ID histórico. A correspondência numérica entre história, spec e atividade inicial é conveniência, não regra de cardinalidade: uma história pode ter várias specs/atividades/handoffs com IDs novos.

## Referências

- Em YAML, `references`, `inputs`, `expected_outputs`, `deliverables`, `related_adrs` e campos `path` usam **caminhos relativos à raiz do repositório**. Saídas futuras são caminhos previstos, não evidência de arquivo existente. Referências de entrada devem existir quando a atividade estiver pronta.
- Em Markdown, links são relativos ao arquivo que os contém. Caminhos de entregáveis futuros aparecem como código, sem links quebrados.
- Dependências e vínculos como `story_id`, `spec_id`, `activity_id`, `epic` usam IDs estáveis. Resolver pelo diretório/catálogo correspondente.
- Nomes de comandos e critérios não são referências de arquivo. Critérios usam `{id: AC-01, criterion: ...}`; `acceptance_mapping` relaciona `criterion_id`, validação e evidência.
- Critérios globais da definição de pronto complementam, mas não substituem, os critérios específicos.

## Estados

| Artefato | Estados permitidos |
|---|---|
| História e épico | `backlog`, `ready`, `in_progress`, `blocked`, `in_review`, `done` |
| Spec | `draft`, `ready`, `superseded` |
| Atividade | `pending`, `in_progress`, `blocked`, `in_review`, `completed`, `cancelled` |
| Handoff | `completed`, `partial`, `blocked` |
| ADR | `proposed`, `accepted`, `superseded`, `deprecated` |

Prioridade: `high`, `medium`, `low`. Estado da spec `ready` significa contrato técnico suficiente, não aceitação do produto. Atividade `pending` pode estar preparada para execução. Handoff `completed` significa conclusão da atividade referida, não de todo o projeto.

`backlog → ready → in_progress → in_review → done` é o caminho normal da história. `blocked` preserva motivo e condição de desbloqueio; voltar ao estado coerente depois da resolução. Revisão pode retornar a `in_progress`. Não alterar para `done` para encerrar uma sessão. Atividade acompanha execução; pode concluir um incremento parcial da história, desde que seu próprio escopo seja validado.

Specs e atividades reais exigem critérios mapeados. Handoffs devem relacionar exatamente a atividade, spec e história usadas; nunca inferir relações somente pela numeração.

## Artefatos sem duplicação excessiva

Índice guarda somente metadados de descoberta. História guarda valor, escopo e aceite. Spec guarda desenho e validação. Atividade guarda execução atribuída. Handoff guarda evidência e continuidade. Questões abertas vivem em `doc/decisions/open-questions.md`; uma spec pode apontar o ID da questão. Não usar YAML como banco de dados de eventos, logs volumosos ou cópia de conversas.
