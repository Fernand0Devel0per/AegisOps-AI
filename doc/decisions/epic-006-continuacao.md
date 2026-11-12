# STORY-060 e EPIC-006 — análise para decisão do PO

Análise documental em 2026-11-12 após o [aceite da STORY-063](story-063-aceite.md). Não altera critérios nem inicia execução. Fontes: [STORY-060](../../roadmap/stories/STORY-060.yaml), [EPIC-006](../../roadmap/epics/EPIC-006.yaml), estudos de [ingestão](../architecture/rich-document-ingestion-results.md) e [recuperação](../architecture/rich-document-retrieval-results.md).

| Gate real | Situação e evidência |
|---|---|
| STORY-060 AC-01: corpus, perguntas, respostas, relevância, evidências, ausências e partições | Evidenciado por RICH-01 e [aceite da STORY-061](story-061-aceite.md). Ausências são relativas ao corpus; grupos são exploratórios, não partição independente ou cega. |
| STORY-060 AC-02: comparação reproduzível de ingestão, chunking e recuperação, métricas e citações por página/seção, com controle de confusão | Há evidências e medições relevantes nas STORY-062/063, incluindo falhas, recursos, controles, denominadores e citações por página. Ainda requer avaliação de suficiência do PO: páginas curtas não produziram comparação efetiva de fronteiras ou sobreposição de chunking; metadados semânticos de seção não foram transportados pelos chunks. Não inferir superioridade de chunking nem suporte automático a seção. |
| STORY-060 AC-03: decisão justificada em ADR sobre manter baseline ou propor tecnologia | Pendente: há recomendação exploratória, mas não há ADR específico que consolide essa decisão agregada. Manter o baseline é opção possível; apresentar evidências, operação e limites. Mudança estrutural exige autorização do PO antes da implementação. |
| STORY-060 DoD | Dependências STORY-050/061/062/063 estão concluídas. A história agregadora permanece em backlog, exige refinamento de contrato, consolidação, validação e revisão dos critérios, além de handoff e estados coerentes. ACT-060 já concluiu somente a preparação; não é contrato de execução agregada. |
| EPIC-006: origem autorizada e citações por página/seção | Origem sintética autorizada e páginas estão evidenciadas; seções constam no corpus de referência, mas o pipeline avaliado não transporta seção semântica automaticamente. Avaliar com o PO se a evidência de página satisfaz a redação página/seção ou se é necessário complementá-la. |
| EPIC-006: comparação medida com falhas de extração e métricas adequadas ao dataset | Evidenciada para o escopo exploratório dos estudos 062/063, com suas falhas, denominadores e limitações; não demonstra desempenho generalizável ou uma comparação efetiva de fronteiras de chunking. |

O épico lista também STORY-060 e continua `in_progress`; STORY-060 continua `backlog`. O pedido atual não autoriza encerrar nenhum dos dois. A redação de AC-02 e do gate de citações deve ser interpretada pelo PO com as limitações concretas, sem supor que outro experimento seja automaticamente obrigatório nem dispensar requisito em nome do PO.

## Alternativas para a próxima decisão

1. **Consolidar primeiro:** autorizar refinamento e trabalho documental da STORY-060 em sua própria branch; rever suficiência de AC-02 e do gate de página/seção; preparar decisão em ADR sobre manter baseline ou propor tecnologia, com revisão humana. Se os critérios e DoD forem demonstrados e o PO autorizar os gates aplicáveis, decidir os encerramentos sem exigir automaticamente outro estudo.
2. **Estudo focado antes da decisão:** se o PO julgar necessária evidência adicional, autorizar escopo, recursos, corpus e protocolo da [proposta experimental](../architecture/rich-document-next-increment-proposal.md); avaliar depois se os resultados resolvem os pontos pendentes. A necessidade de uma nova história é decisão de planejamento, não pressuposto.
3. **Estudo posterior e independente:** concluir a consolidação e os gates se forem considerados atendidos, e planejar pesquisa posterior separadamente, sem condicionar o épico indefinidamente a uma possível melhoria.

Escolha recomendada para discussão: primeiro decidir a suficiência dos gates e autorizar ou não a consolidação; usar o estudo focado apenas se necessário para o requisito ou se houver interesse próprio de pesquisa. Nenhuma alternativa foi executada nem aprovada por este documento.
