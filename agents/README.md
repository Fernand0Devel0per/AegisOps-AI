# Contratos de trabalho e continuidade

Comece por [AGENTS.md](../AGENTS.md). Esta pasta guarda estado versionável, não conversas completas nem código de aplicação.

| Pasta | Conteúdo |
|---|---|
| `specs/` | Solução técnica por história, interfaces necessárias, decisões e mapeamento dos critérios para validações |
| `activities/` | Atribuição delimitada: objetivo, entradas, saídas, restrições, passos e validação |
| `handoffs/` | Estado real ao interromper ou encerrar: arquivos, motivos, evidências, falhas e próximo passo |
| `templates/` | Modelos YAML para novos contratos |

O bootstrap histórico está registrado em [SPEC-000](specs/SPEC-000.yaml), [ACT-000](activities/ACT-000.yaml) e [HANDOFF-000](handoffs/HANDOFF-000.yaml). A [SPIKE-030](../roadmap/stories/SPIKE-030.yaml) e [ACT-029](activities/ACT-029.yaml) foram concluídas; [HANDOFF-029](handoffs/HANDOFF-029.yaml) registra o aceite, a validação e as pendências para as histórias futuras.

A [STORY-030](../roadmap/stories/STORY-030.yaml) está concluída: [SPEC-030](specs/SPEC-030.yaml), [ACT-030](activities/ACT-030.yaml) e [HANDOFF-030](handoffs/HANDOFF-030.yaml) registram o corpus, o aceite do PO e as limitações futuras.

## Regras de handoff

- Nenhuma atividade é `completed` sem validação executada e evidência registrada. Caso parcial/bloqueado deve usar o estado correspondente.
- Informar comando ou procedimento, resultado e caminho da evidência; não confundir revisão documental com testes da aplicação.
- Identificar testes não executados e motivo. Não esconder falha conhecida, dúvida ou trabalho pendente.
- Em `changed_files`, registrar caminho e motivo. Para muitos arquivos uniformes, listar cada caminho e apontar a justificativa comum; evitar copiar conteúdo de documentos ou código.
- Identificar o próximo papel/atividade, entradas necessárias e próximo passo concreto. Handoff para um papel não significa que uma mensagem foi enviada ou um agente foi iniciado.
- Versionar contratos, atualizações do roadmap e evidências com a entrega Git. Nunca afirmar commit/CI/publicação se não aconteceram.

Estados e convenções estão em [conventions.md](../doc/standards/conventions.md). O fluxo completo está em [workflow.md](../doc/standards/workflow.md).

A [STORY-031](../roadmap/stories/STORY-031.yaml) foi concluída e integrada no PR 8; [SPEC-031](specs/SPEC-031.yaml), [ACT-031](activities/ACT-031.yaml) e [HANDOFF-031](handoffs/HANDOFF-031.yaml) registram a entrega e continuidade.

O EPIC-003 foi encerrado após o merge informado e pedido do PO; o [HANDOFF-031](handoffs/HANDOFF-031.yaml) registra o fechamento. A [STORY-040](../roadmap/stories/STORY-040.yaml) foi concluída após aceite conjunto do PO: [SPEC-040](specs/SPEC-040.yaml), [ACT-040](activities/ACT-040.yaml) e [HANDOFF-040](handoffs/HANDOFF-040.yaml) registram escopo e limitações. A [STORY-041](../roadmap/stories/STORY-041.yaml) tem incremento parcial integrado pelo PR 9; permanece em andamento com critérios pendentes. O PO autorizou a STORY-050 por exceção documentada, preservando as pendências da STORY-041 e o EPIC-004 em andamento; consulte [HANDOFF-041](handoffs/HANDOFF-041.yaml) e [transição](../doc/decisions/story-050-excecao-dependencia.md).

A [STORY-050](../roadmap/stories/STORY-050.yaml) foi concluída por autorrevisão após estudo offline e seu encerramento foi ratificado pelo PO; a vertical atual foi mantida e o protótipo não foi adotado. O [HANDOFF-050](handoffs/HANDOFF-050.yaml) registra limites e evidências; o EPIC-005 estava em andamento naquele handoff; sua auditoria posterior está registrada abaixo.

O [EPIC-005](../roadmap/epics/EPIC-005.yaml) foi encerrado após auditoria e autorização do PO; a decisão do ADR-0007 e as pendências do EPIC-004 permanecem. A [STORY-060](../roadmap/stories/STORY-060.yaml) agrega incrementos propostos [061](../roadmap/stories/STORY-061.yaml), [062](../roadmap/stories/STORY-062.yaml) e [063](../roadmap/stories/STORY-063.yaml). O [HANDOFF-060](handoffs/HANDOFF-060.yaml) registra a preparação; a STORY-061 foi concluída após aceite humano conforme [HANDOFF-061](handoffs/HANDOFF-061.yaml). A STORY-062 foi concluída após aceite do PO, conforme [HANDOFF-062](handoffs/HANDOFF-062.yaml). A STORY-063 foi concluída após aceite humano, separado da autorrevisão, conforme [HANDOFF-063](handoffs/HANDOFF-063.yaml) e [registro de aceite](../doc/decisions/story-063-aceite.md). STORY-060 e EPIC-006 seguem abertos; seus gates e alternativas estão na [análise de continuidade](../doc/decisions/epic-006-continuacao.md). ACT-060 já concluiu a preparação; uma execução agregada precisa de contrato refinado e autorização.
