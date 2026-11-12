# Aceite humano — STORY-062, estudo exploratório de RICH-01

Em **2026-11-12**, o Product Owner aprovou nesta conversa os resultados exploratórios da comparação de Poppler textual, pdfplumber e chunking sobre RICH-01 v1.0.0. O PO aceitou as conclusões e limitações documentadas e as medições como medições locais do executor. Esse aceite é posterior e separado da autorrevisão semântica do executor em [semantic-review.yaml](../../datasets/rich-document-experiment/semantic-review.yaml); os julgamentos originais não foram reescritos para atribuir a eles uma aprovação anterior.

## Identificação dos artefatos avaliados

O escopo é o conteúdo versionado no commit local `c1d0a61`, incluindo o protocolo congelado anteriormente no commit `2a4cdb6`. Valores SHA-256 conferidos no encerramento:

| Artefato | SHA-256 |
|---|---|
| [Relatório da execução](../architecture/rich-document-ingestion-results.md) | `368abeddcf151dc9d8e1cd0af9104972e5fa24290441598ed8f00b748477ab09` |
| [Protocolo congelado](../../datasets/rich-document-experiment/protocol.md) | `bf98f432fa17057f06f0b9050b432c40217d57cc770c1336e588fe2a8e79907b` |
| [Autorrevisão por caso](../../datasets/rich-document-experiment/semantic-review.yaml) | `8293cb11c90d41ed171f805ad2ba91df519f328164d913466f958b39e0b4f683` |
| [Métricas](../../datasets/rich-document-experiment/output/evaluation.json) | `42ebdffe030aac85533126563c28b6661309b6d872249533347c7727909e418d` |
| [Medições individuais](../../datasets/rich-document-experiment/output/measurements.json) | `ed3ebd54ea2285797e198180fbcf4d92a44185b168b5aaf1a6f8df1525b68a23` |
| [Índice das extrações](../../datasets/rich-document-experiment/output/extraction-freeze.json) | `5d7dd517b0a7b45e79a1da3a6b2ae2d982cc96b8560cb3dd49e963a57cb72928` |
| [Índice dos chunks](../../datasets/rich-document-experiment/output/chunk-freeze.json) | `8aad19af2e30cd4ce11dbac0cf0081a62094ee4af395d245edab16bf748b6eb2` |
| [Inventário e hashes do código](../../datasets/rich-document-experiment/output/dependency-inventory.json) | `5e4f37384c3480ff3a5ee236375106115cf28b12b9afc94efdb3fc0064deeb70` |
| [Preflight de isolamento](../../datasets/rich-document-experiment/output/preflight.json) | `9f2989a8999963b95045cb65a55b3dc6c2aad98112da2c2a32bd08c484c2df3c` |
| [Sondas de falha e timeout](../../datasets/rich-document-experiment/output/failure-probes.json) | `ea8cc219b8632222493086fbae5f34410566ea54eca6393f99e9941dbe2777e7` |

Os índices vinculam, respectivamente, 15 extrações e 15 arquivos de chunks por seus hashes. Os hashes do manifesto, das perguntas, dos gabaritos e dos cinco PDFs são os registrados no [aceite da STORY-061](story-061-aceite.md) e foram verificados novamente. O inventário vincula os scripts e o protocolo aos respectivos hashes. Versões, parâmetros, tentativas, falhas, repetições e mecanismos de isolamento permanecem nos arquivos históricos do experimento.

## Resultados aceitos e limites

| Indicador | Poppler textual | pdfplumber |
|---|---:|---:|
| Ocorrências pergunta-âncora preservadas | 11/15 | 13/15 |
| Perguntas com evidências e relações suficientes | 7/11 | 9/11 |
| Relações tabulares | 0/2 | 2/2 |
| Associações entre serviços e orientações nas colunas | 0/2 | 0/2 |

O PO reconheceu a melhor preservação tabular pelo pdfplumber **neste corpus**, a ambiguidade das duas colunas, a utilidade visual do diagnóstico `-layout` sem estrutura semântica nativa, a ausência de hierarquia semântica automática, a perda dos metadados nativos da tabela nos chunks e a dependência de Q10 de páginas distintas.

O PO registrou que o corpus é pequeno, todas as páginas tinham menos de 600 caracteres e não se demonstrou superioridade do chunking estrutural, divisão significativa nem sobreposição efetiva. Medições são locais, com overhead e limites descritos no relatório, e não são benchmark generalizável. Uma comparação futura de chunking exige documentos suficientemente extensos e julgamentos próprios. Palavras presentes ou citações resolvíveis não comprovam suporte semântico; texto, relação sustentada, tabela nativa, estrutura transportada e proveniência devem continuar distintos.

Este aceite não adota pdfplumber para produção, não demonstra superioridade geral, não aprova Docling, embeddings, bancos vetoriais, RAG, inferência real nem mudanças da API ou Colibri. Alterações futuras não devem modificar a configuração histórica do estudo.

## Conferência de critérios e Definition of Done

| Critério | Evidência e conclusão |
|---|---|
| AC-01 | [Protocolo](../../datasets/rich-document-experiment/protocol.md), [ambiente](../../datasets/rich-document-experiment/output/environment.json), [preflight](../../datasets/rich-document-experiment/output/preflight.json), hashes e falhas registram entradas, versões, configuração e limites. |
| AC-02 | [Relatório](../architecture/rich-document-ingestion-results.md), [autorrevisão](../../datasets/rich-document-experiment/semantic-review.yaml) e [métricas por caso](../../datasets/rich-document-experiment/output/evaluation.json) julgam texto, relações, contexto e proveniência, inclusive ausência de seção, inviabilidade e denominadores. |
| AC-03 | [Medições individuais](../../datasets/rich-document-experiment/output/measurements.json), [testes](../../datasets/rich-document-experiment/test_pipeline.py) e [handoff](../../agents/handoffs/HANDOFF-062.yaml) registram método, recursos, repetição, reprodução e limitações. |
| DoD | Evidência por AC, validações e limites, aceite posterior do PO, handoff versionável e atualização conjunta dos estados da história, atividade e índice. |

O PO informou seu aceite; o agente não observa nem reconstitui independentemente o processo de revisão humana. A reprodução e os testes comprovam apenas o escopo exercitado, não corrigem as limitações de amostra, extração ou método.
