# STORY-063 — avaliação exploratória de recuperação e citações

Estado em 2026-11-12: execução local concluída e **em revisão do PO**. O corpus é sintético, pequeno e previamente exposto; não há teste independente ou cego. Os julgamentos semânticos são autorrevisão do executor, baseada na revisão da STORY-062 aceita pelo PO, e não constituem aceite humano desta entrega. Não houve gerador, inferência ou avaliação de qualidade de respostas geradas.

## Método e rastreabilidade

[Protocolo](../../datasets/rich-document-retrieval/protocol.md) congelado no commit local `49bad30` antes de qualquer ranking. B1 usa Poppler textual + chunks fixos históricos; C1 usa pdfplumber + chunks fixos históricos. Ambos recebem as mesmas 13 consultas, ranking, k e orçamento. Nenhum PDF, extração ou chunk histórico foi regenerado ou modificado. D1 (`-layout`) e transporte de metadados foram excluídos desta rodada; alternativas estão em [proposta de metadados](story-063-metadata-options.md).

Antes de RICH-01, o [teste C1](../../datasets/rich-document-retrieval/output/equivalence-c1.json) comparou o adaptador ao mecanismo original, com corpus C1 verificado por suas próprias regras: 10 consultas × k de 1 a 5, mais 32 casos de normalização, ausência e invalidez, empate controlado e falhas de integridade. IDs, scores, ordem, cortes e estados coincidiram. `src/aegisops/retrieval.py` e seu corpus não foram alterados. Os números antigos do C1 não são comparáveis diretamente aos resultados dos PDFs.

O ranker recebeu somente pares ID/texto, parâmetros e texto da consulta; os IDs codificam documento e página, mas registros externos de proveniência, gabaritos, fontes e justificativas não foram montados no sandbox. O controlador externo preparou IDs e proveniência, mas não enviou esses metadados extras ao ranker. Os [rankings](../../datasets/rich-document-retrieval/output/rankings.json) e contexto foram congelados com [hashes](../../datasets/rich-document-retrieval/output/ranking-freeze.json) antes de o avaliador abrir `judgments.yaml` e a revisão 062. Esta é uma separação efetivamente aplicada ao experimento, não uma garantia geral de segurança. Após o congelamento, o executor criou [revisão semântica](../../datasets/rich-document-retrieval/output/semantic-review.json); cálculos e [resultados individuais](../../datasets/rich-document-retrieval/output/evaluation.json) são separados dela.

A unidade de julgamento é a ocorrência pergunta-âncora: 11 positivas, 15 ocorrências, incluindo quatro consultas multiâncora. A presença de palavras é condição necessária, não suficiente; a elegibilidade semântica e o contexto da relação seguem a revisão 062. Âncoras perdidas na extração permanecem no denominador e contam como não cobertas. Consulta com falha técnica seria separada; não houve falha técnica nesta rodada.

## Recuperação

As duas configurações produziram **IDs, scores e ordem idênticos** para as 26 combinações de consulta/k. A diferença de cobertura abaixo decorre das relações preservadas na representação de entrada, especialmente tabela, não de mudança de chunking ou de ranking. Recall é média das frações por pergunta; o numerador fracionário não é contagem de âncoras. MRR usa o primeiro trecho com ao menos uma âncora e contexto suficiente: relevância parcial não implica resposta completa.

| Configuração | k | Recall soma/11 | MRR soma/11 | Ocorrências cobertas/15 | Perguntas integrais/11 | Multiâncora integrais/4 |
|---|---:|---:|---:|---:|---:|---:|
| B1 Poppler fixo | 3 | 7,5/11 = 0,6818 | 9/11 = 0,8182 | 10/15 | 6/11 | 1/4 |
| B1 Poppler fixo | 5 | 8/11 = 0,7273 | 9/11 = 0,8182 | 11/15 | 7/11 | 2/4 |
| C1 pdfplumber fixo | 3 | 9,5/11 = 0,8636 | 11/11 = 1,0000 | 12/15 | 8/11 | 1/4 |
| C1 pdfplumber fixo | 5 | 10/11 = 0,9091 | 11/11 = 1,0000 | 13/15 | 9/11 | 2/4 |

Esses números são iguais antes e depois do orçamento. Todas as 52 saídas couberam inteiramente; uso máximo observado, incluindo cabeçalhos `[ID]` e quebras de linha, foi 1.697/1.800 caracteres, sem truncamento. Portanto não se mediu perda real por truncamento neste corpus; o teste sintético cobre corte de âncora. A seção, o hash, a página e os offsets são resolvidos pelo avaliador fora da representação entregue e não foram contados como texto enviado.

Por consulta, `cobertas/total; r` abaixo indica cobertura e primeiro rank relevante. Q12/Q13 são ausências, não denominadores de Recall/MRR. Os IDs, scores, ordem, justificativas, citações e versões bruta e limitada estão nos [resultados por consulta](../../datasets/rich-document-retrieval/output/evaluation.json).

| Pergunta | B1 @3 | B1 @5 | C1 @3 | C1 @5 |
|---|---:|---:|---:|---:|
| Q01 | 1/1; 1 | 1/1; 1 | 1/1; 1 | 1/1; 1 |
| Q02 | 1/1; 1 | 1/1; 1 | 1/1; 1 | 1/1; 1 |
| Q03 | 1/1; 1 | 1/1; 1 | 1/1; 1 | 1/1; 1 |
| Q04 | 0/1; — | 0/1; — | 1/1; 1 | 1/1; 1 |
| Q05 | 0/1; — | 0/1; — | 1/1; 1 | 1/1; 1 |
| Q06 | 1/2; 1 | 1/2; 1 | 1/2; 1 | 1/2; 1 |
| Q07 | 1/2; 1 | 1/2; 1 | 1/2; 1 | 1/2; 1 |
| Q08 | 1/1; 1 | 1/1; 1 | 1/1; 1 | 1/1; 1 |
| Q09 | 1/1; 1 | 1/1; 1 | 1/1; 1 | 1/1; 1 |
| Q10 | 1/2; 1 | 2/2; 1 | 1/2; 1 | 2/2; 1 |
| Q11 | 2/2; 1 | 2/2; 1 | 2/2; 1 | 2/2; 1 |
| Q12 | retorno; relacionado insuficiente | retorno; relacionado insuficiente | retorno; relacionado insuficiente | retorno; relacionado insuficiente |
| Q13 | retorno; relacionado insuficiente | retorno; relacionado insuficiente | retorno; relacionado insuficiente | retorno; relacionado insuficiente |

Q04/Q05 são 0/1 em B1: a saída Poppler linearizada não demonstra as relações de tabela; C1 mantém linhas textuais suficientes, embora os chunks não carreguem metadados nativos de células. Q06/Q07 têm apenas a âncora do sinal, não a associação inequívoca da orientação ao serviço, em ambas as configurações. Assim, o MRR de C1 é 1,0 mesmo com apenas 9/11 perguntas integrais no top 5: os primeiros resultados podem ser apenas parcialmente relevantes.

Q10 retorna RD-05 p. 1 em primeiro e p. 2 em quarto, em ambas as configurações: 1/2 âncoras no top 3 e 2/2 no top 5, com vínculo OR-7 conferido e duas citações de página resolvíveis. Não se exige união em um chunk. Q12 retorna um trecho de Atlas e Q13 um trecho de Lume, relacionados mas insuficientes para o limite de deadlock e o endereço IP. Nas duas configurações e cortes, há retorno em 2/2 ausências, abstenção em 0/2 ausências e abstenção positiva em 0/11. Retorno relacionado não é automaticamente afirmação falsa, e não houve resposta gerada.

## Citações e afirmações

Cada referência contém documento, versão, SHA-256 do PDF, página, ID de chunk e intervalo semiaberto na extração congelada, incluindo o trecho efetivamente disponível após o orçamento; seção não sustentada é `null`. Por configuração, 39/39 citações no top 3 e 64/64 no top 5 foram tecnicamente resolvíveis. Contagens são ocorrências por consulta, incluindo as duas ausências, não documentos únicos.

| Configuração | k | Citações com ao menos uma âncora sustentada / citações semanticamente julgadas | Não julgadas |
|---|---:|---:|---:|
| B1 | 3 | 9/13 | 26 |
| B1 | 5 | 10/14 | 50 |
| C1 | 3 | 11/13 | 26 |
| C1 | 5 | 12/14 | 50 |

As demais citações julgadas foram insuficientes para a relação ou para as ausências; trechos não julgados não viram negativos. Uma citação que sustenta uma âncora pode apoiar apenas parte da pergunta. Afirmações completas dos gabaritos foram sustentadas em 6/11 e 7/11 para B1, ou 8/11 e 9/11 para C1, respectivamente em k=3 e k=5, sob a autorrevisão registrada. Nenhuma afirmação de LLM foi produzida ou avaliada.

## Recursos e integridade

O [preflight](../../datasets/rich-document-retrieval/output/preflight.json) comprovou namespace de rede distinto com loopback isolado, sem acesso ao loopback do host, raiz e `/dev` somente leitura, tmpfs somando 100 MiB, afinidade de um núcleo, cgroup CPU 100% e memória agregada máxima de 1 GiB. Foi reutilizado sem alteração o supervisor da STORY-062; limite de 30 s por operação, 200 chunks/configuração e 1 MiB de texto/documento. Nenhuma instalação, GPU, OCR, rede, inferência ou serviço pago foi usada no processamento.

O ambiente foi Fedora Linux, Python 3.14.8, Intel Core i5-1235U, systemd 258 e bubblewrap 0.12.0; detalhes em [ambiente](../../datasets/rich-document-retrieval/output/environment.json) e [máquina](../../datasets/rich-document-retrieval/output/environment-notes.json). Houve um aquecimento e três repetições por operação: três medições de índice por configuração e 78 medições de consulta por configuração (13 perguntas × 2 k × 3); 216 execuções ao incluir aquecimentos, todas bem-sucedidas. Os dados individuais e o tempo interno estão em [measurements.json](../../datasets/rich-document-retrieval/output/measurements.json). Parede inclui inicialização do sandbox, Python e serialização; memória é pico agregado incluindo supervisor. Os tempos são observações locais, não benchmark de escalabilidade.

| Configuração/operação | Parede média (ms) | Faixa parede (ms) | CPU média (ms) | Pico agregado máx. (MiB) |
|---|---:|---:|---:|---:|
| B1 índice, n=3 | 26,284 | 24,972–27,314 | 25,876 | 13,34 |
| C1 índice, n=3 | 26,309 | 25,945–26,743 | 25,096 | 13,42 |
| B1 consulta, n=78 | 26,021 | 23,921–34,454 | 25,118 | 13,85 |
| C1 consulta, n=78 | 26,926 | 25,259–40,628 | 25,925 | 13,83 |

Os índices têm seis chunks cada e 150 termos únicos; JSON UTF-8 compacto do índice — incluindo IDs, textos e listas de termos — tem 4.049 bytes em B1 e 3.957 em C1. Não representa memória do índice nem tamanho de um banco. Repetições tiveram saídas determinísticas; `ranking-freeze.json` protege rankings e medições; o avaliador confere hashes do corpus e das saídas históricas antes de ler julgamentos. Referências individuais não provam verdade externa nem suporte semântico sem a revisão registrada.

## Recomendação e limites

Para este conjunto, C1 + fixo cobriu mais relações julgadas do que B1 + fixo, mas os rankings foram idênticos e a diferença vem da extração tabular; não há evidência de superioridade geral, de chunking ou de arquitetura. Ambas as representações falharam na associação das colunas; Q10 só ficou integral no top 5. O orçamento não foi exercitado de modo a causar perda, e Q12/Q13 não geraram abstenção apesar da ausência aprovada.

Recomenda-se revisar estes resultados e, somente após decisão específica, estudar transporte de estrutura tabular, proveniência e documentos mais longos com julgamentos próprios. Sidecar e texto enriquecido têm trade-offs separados na [proposta](story-063-metadata-options.md); nenhum foi escolhido ou implementado. O conjunto exposto e pequeno, âncoras dependentes e medições com overhead impedem generalização. STORY-063 permanece em revisão até aceite explícito; STORY-060 e EPIC-006 continuam abertos.
