# Aceite humano — STORY-063, recuperação e citações exploratórias

Em **2026-11-12**, o Product Owner aprovou nesta conversa os resultados exploratórios B1/C1 sobre RICH-01 v1.0.0, com as ressalvas abaixo. Trata-se do aceite humano posterior e separado da [autorrevisão do executor](../../datasets/rich-document-retrieval/output/semantic-review.json); o aceite não altera nem reinterpreta retroativamente esses julgamentos. O agente registra a declaração do PO, sem afirmar que observou independentemente como ele realizou a revisão.

## Artefatos e integridade

O protocolo foi congelado no commit local `49bad30`; a execução e seus resultados estão no commit `8dbbf82`, descendente daquele, na branch `feat/story-063`. Na conclusão, foram conferidas a ancestralidade, a ausência de diferenças dos artefatos históricos e as cadeias de hashes. SHA-256 dos arquivos aceitos:

| Artefato | SHA-256 |
|---|---|
| [Relatório](../architecture/rich-document-retrieval-results.md) | `2043037b7e07eea1c2bb2a4863b174485f8d5172ce19cccb0d98027106da988a` |
| [Protocolo](../../datasets/rich-document-retrieval/protocol.md) | `197bd75a5c927767dd0a91906f03198f8fefa960de2dad711a111a8d11fedbdf` |
| [Equivalência C1](../../datasets/rich-document-retrieval/output/equivalence-c1.json) | `5a80028f163e45e7f6da8602adad2b86b9033a4ae2efa06e6875ce13b828068e` |
| [Índice congelado](../../datasets/rich-document-retrieval/output/ranking-freeze.json) | `528fa7f41ec5210024e0dc101bb45fdc89af7e99e05dc364baa2a5e03f7ca711` |
| [Rankings](../../datasets/rich-document-retrieval/output/rankings.json) | `3144f33ef514f876330bae6834db5be5488d82bcf0c80e55a86d3b07026ee356` |
| [Proveniência](../../datasets/rich-document-retrieval/output/provenance.json) | `a9fa5c8b4c8c7e20911b2e2a137a116f9cbb21df045d375cedd274c314f0cac8` |
| [Estatísticas do índice](../../datasets/rich-document-retrieval/output/index-statistics.json) | `c6dc7d60f429eaa3c42f157b959501f6801ca5d1d7fa56c11b7d99a18abb36ff` |
| [Medições](../../datasets/rich-document-retrieval/output/measurements.json) | `d22add88a183e9b29bb493003fa38c528e8883ac02b319926aa8bbe7720934aa` |
| [Ambiente](../../datasets/rich-document-retrieval/output/environment.json) | `1023c054b27bb3b354d90532ce5e940ae78cbaf812cc4aced4f3b902d5133120` |
| [Autorrevisão](../../datasets/rich-document-retrieval/output/semantic-review.json) | `59ee8d10030eed452821164cfb2a41f5d18f158008deef80f370e431df1c6b9a` |
| [Avaliação](../../datasets/rich-document-retrieval/output/evaluation.json) | `5778b0d80a4d52d09ed3a2368b97d332f3ab0c5df4a75acc60ec24b7aa066a7b` |
| [Preflight](../../datasets/rich-document-retrieval/output/preflight.json) | `334b6297336ad831bdd4024f19e8362ef1d0b9a31a3e5ac0b3c5c7b2eb9c58e6` |

O índice congelado vincula os cinco arquivos de ranking, proveniência, estatísticas, medições e ambiente ao protocolo. O ambiente vincula os scripts, o corpus e os índices da STORY-062; os dois índices vinculam 15 extrações e 15 arquivos de chunks. Foram conferidos os cinco PDFs contra o manifesto e os vínculos entre índice, autorrevisão e avaliação. Os julgamentos, relatórios e resultados históricos permanecem intactos.

## Resultados e ressalvas aceitos

| Configuração | Recall@3 | Recall@5 | MRR@3 e @5 | Perguntas integralmente sustentadas @5 |
|---|---:|---:|---:|---:|
| B1: Poppler textual e chunk fixo | 7,5/11 = 0,6818 | 8/11 = 0,7273 | 9/11 = 0,8182 | 7/11 |
| C1: pdfplumber e chunk fixo | 9,5/11 = 0,8636 | 10/11 = 0,9091 | 11/11 = 1,0000 | 9/11 |

C1 sustentou melhor as evidências neste corpus pela preservação das relações tabulares na representação extraída; os 52 rankings têm os mesmos IDs, scores e ordem entre B1 e C1 por pergunta e corte. Não há evidência de melhoria do algoritmo lexical ou do chunking. MRR mede posição da primeira âncora relevante, não a suficiência integral da resposta. Q06/Q07 continuam parciais por ambiguidade entre colunas; Q10 depende de duas páginas, com cobertura completa apenas no top 5.

Citações resolvíveis não demonstram suporte semântico: por configuração, 39/39 referências em top 3 e 64/64 em top 5 foram resolvíveis. Das 13 julgadas em top 3, 9 sustentam âncora em B1 e 11 em C1, com 26 não julgadas; em top 5, 10/14 em B1 e 12/14 em C1 sustentam âncora, com 50 não julgadas. Não julgadas não são positivas nem negativas. Q12/Q13 retornaram trechos relacionados, insuficientes, sem abstenção lexical; retorno relacionado não é por si resposta falsa e abstenção não provaria ausência semântica.

Os contextos couberam nos 1.800 caracteres, com máximo observado de 1.697: não se observou truncamento real. Corpus pequeno, sintético e exposto ao executor não é teste independente ou cego. Custos e tempos locais incluem overhead e não são demonstração de escalabilidade, qualidade geral de RAG ou resposta de LLM. Este aceite não adota arquitetura, ferramenta ou dependência e não autoriza alteração da aplicação.

## Critérios e Definition of Done

| Critério | Evidência e conclusão |
|---|---|
| AC-01 | [Protocolo](../../datasets/rich-document-retrieval/protocol.md), equivalência C1 e rankings congelados documentam baseline e controles; diferenças de extração e limitações são discriminadas. |
| AC-02 | [Relatório](../architecture/rich-document-retrieval-results.md), [avaliação](../../datasets/rich-document-retrieval/output/evaluation.json) e medições registram métricas, denominadores, ausências, recursos e limitações por configuração. |
| AC-03 | Relatório revisado e [opções conceituais](../architecture/story-063-metadata-options.md) apresentam limites e recomendação sem adoção estrutural. |
| DoD | Evidência por critério, validações e limites no [handoff](../../agents/handoffs/HANDOFF-063.yaml), aceite humano posterior e estados sincronizados. |

As conferências de integridade e as validações documentais do encerramento não são reexecução do experimento. Testes e avaliações executados anteriormente são os registrados no handoff histórico. A [análise dos gates](epic-006-continuacao.md) mantém separadas as decisões sobre STORY-060 e EPIC-006.
