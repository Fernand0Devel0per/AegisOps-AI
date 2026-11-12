# Consolidação — STORY-060 e EPIC-006

Em 2026-11-12, após a análise dos gates e os aceites dos incrementos, o PO solicitou fechar a história e o épico e abrir um PR para sua conferência. Este documento consolida as evidências para a proposta de encerramento na branch; a revisão humana do PR e deste documento ainda não ocorreu. Não se atribui ao PO revisão específica ou resultados adicionais que ele não declarou. A [análise anterior](../decisions/epic-006-continuacao.md) preserva o estado anterior à solicitação.

## Evidências por critério da STORY-060

| Critério | Evidência, conclusão e limite |
|---|---|
| AC-01 — corpus e julgamentos | [Aceite 061](../decisions/story-061-aceite.md), [manifesto](../../datasets/rich-documents/manifest.yaml), [perguntas](../../datasets/rich-documents/questions.yaml) e [gabaritos](../../datasets/rich-documents/judgments.yaml): cinco PDFs sintéticos, seis páginas, perguntas, âncoras e ausências relativas à versão. Grupos são exploratórios e não constituem partição independente. |
| AC-02 — comparação, citações e controles | [Aceite 062](../decisions/story-062-aceite.md), [ingestão](rich-document-ingestion-results.md), [aceite 063](../decisions/story-063-aceite.md) e [recuperação](rich-document-retrieval-results.md): extrações e configurações de chunking foram comparadas no corpus sob parâmetros e hashes registrados; resultados, falhas, denominadores e recursos foram documentados; o ranking foi comparado em B1/C1 com mesmos parâmetros. As páginas são citadas; os chunks não produziram metadados semânticos de seção (cobertura 0/6). As estratégias de chunking geraram os mesmos trechos no recorte aplicável: não houve divisão significativa nem sobreposição efetiva, logo não se mediu seu efeito. O critério é apresentado para revisão do PO com essas limitações, sem converter evidência insuficiente em superioridade ou em capacidade de seção. |
| AC-03 — decisão em ADR | [ADR-0008](../adr/0008-documentos-ricos-manter-baseline.md) fundamenta manter o baseline já existente e não adotar tecnologia nova. A decisão técnica não declara aprovação humana prévia do ADR; mudança estrutural futura exige aprovação e ADR apropriado. |

Os resultados aceitos incluem B1/C1 com recall@5 de 8/11 e 10/11 e 7/11 e 9/11 perguntas integralmente sustentadas, respectivamente. A diferença decorre da representação extraída, não de mudança no ranking ou chunking. MRR mede a primeira âncora e não suficiência. Q10 requer duas páginas; Q06/Q07 são parciais; Q12/Q13 retornaram documentos relacionados e insuficientes, sem abstenção lexical. Resolvibilidade técnica não é suporte semântico; itens não julgados não são negativos. Nenhum contexto real foi truncado no orçamento de 1.800 caracteres.

## Critérios de saída do EPIC-006

- **Origem e citações por página/seção:** PDFs sintéticos têm origem autorizada e hashes. Há citações por página nos resultados e seções identificadas no corpus de referência; não há suporte automático a seção nos chunks testados. A evidência apresentada para o gate é por página; não se afirma implementação de citações de seção.
- **Comparação medida, falhas e métricas:** os estudos 062/063 registram medidas, falhas, critérios, denominadores e controles para o corpus exploratório. Fatores não exercitados e confusão residual são explicitados acima e nos relatórios. A avaliação não é benchmark independente nem demonstra qualidade geral de RAG.

STORY-061/062/063 estão concluídas após aceites próprios. A decisão de encerramento proposta para STORY-060 e EPIC-006 é rastreada no handoff desta consolidação e submetida ao PR para conferência do PO. Testes documentais e de integridade deste fechamento não constituem nova execução experimental. Permanecem sem aprovação a integração dos experimentos, nova dependência, inferência real e nova arquitetura.

## Continuidade

A [pesquisa futura de metadados e documentos longos](rich-document-next-increment-proposal.md) continua opcional e exige autorização própria; não é dependência automaticamente criada para este encerramento. A próxima fase não é iniciada por este PR.
