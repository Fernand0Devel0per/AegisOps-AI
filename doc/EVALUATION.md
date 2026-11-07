# Avaliação exploratória da recuperação lexical — protocolo congelado

Congelado antes de inspecionar qualquer ranking da STORY-031. Corpus `C1-2026-11-04.1`, SHA-256 agregado `562b1a8bf10a96ce8f83d41dd43ad102256e5c006bc44c67d78b3a31f691c3cb`; manifesto SHA-256 `63fadc27c030b0647db84d63fa1fc7b93b31af069638af2560e7fdecffa34b30`. Julgamentos `C1-queries-2026-11-04.1`, bytes de `queries.yaml` SHA-256 `cfbb5f70cb669cacff739c4317c3fce7c5818386267dbe5f35d93888d2612f8b`. Fonte e revisão conjunta: [dataset](../datasets/evaluation/README.md) e [revisão](../datasets/evaluation/REVIEW.md).

Unidade: todo o conteúdo após `## Excerpt` em cada arquivo. Apenas esse texto participa da busca. Normalização: NFKD, remover marcas Unicode, casefold e segmentar sequências alfanuméricas; sem stemming, tradução, sinônimos, stopwords ou ponderação. Pontuação: quantidade de termos distintos em comum entre consulta e trecho. Selecionar apenas pontuação positiva, ordem decrescente e desempate por ID ascendente; mostrar até k=5, com prefixo de 3 para Recall@3. Busca aceita k inteiro de 1 a 5. Nenhuma coincidência produz abstenção explícita; erro de entrada ou corpus é falha, nunca abstenção. Consulta de até 4096 caracteres deve conter termo alfanumérico. Retorno inclui texto e ID, caminho, versão local e fonte e versão originais, com integridade verificada. Nenhum dado de julgamento entra no ranking.

As 10 consultas revisadas são exploratórias, sem separação desenvolvimento/teste ou ajuste por resultado: três incidentes independentes e uma necessidade hipotética não permitem divisão representativa. Cada tradução e variante de INC-003 permanece no mesmo grupo; Q09/Q10 são uma única necessidade hipotética, com ausência julgada somente neste corpus. Não há teste independente. Não julgados permanecem não julgados.

Recall@k por consulta positiva é relevantes distintos retornados nos primeiros k / todos os relevantes julgados; média sobre positivas. Primeiro relevante e MRR usam horizonte 5 e zero nos misses; apresentar numeradores, denominadores e casos sem julgamento. Para ausências julgadas, retorno indevido e abstenção correta usam o total de ausências; para positivas, registrar abstenções indevidas. Erros técnicos são relatados separadamente, sem classificá-los como abstenção. Apresentar por idioma e grupo, com pares pt→en e en→en. Não há meta ou presunção sobre idiomas. Resultados serão acrescentados após execução, sem alteração desta política.

## Execução exploratória

Executada localmente em 2026-11-05 com pacote não editável, sem alterar corpus ou julgamentos. Dados completos reproduzíveis em [results-c1-lexical.json](../datasets/evaluation/results-c1-lexical.json). Com PyYAML disponível no Python do sistema e ambiente instalado conforme [desenvolvimento](DEVELOPMENT.md), reproduza com `python3 datasets/evaluation/measure.py`; o script verifica hashes e revisão estrutural e chama `.venv/bin/python` a partir de `/tmp`. Falhas técnicas, se ocorrerem, ficam fora dos denominadores de saídas válidas e são contadas; nesta execução não houve exclusões.

Os numeradores de recall são somas dos recalls por consulta (não quantidade de acertos), e os de MRR são somas dos recíprocos. Os contadores de negativos e não julgados são ocorrências entre todos os trechos exibidos em até cinco posições, não consultas. O denominador zero é indicado por —.

| Corte | Consultas | Recall@3 soma/n | Recall@5 soma/n | MRR@5 soma/n | Abstenção positiva | Retorno em ausência | Abstenção em ausência | Não julgados @5 | Negativos @5 | Falhas técnicas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Total | 10 | 5.5/8 = 0.6875 | 7.5/8 = 0.9375 | 5.83333/8 = 0.7292 | 0/8 | 1/2 | 1/2 | 15 | 14 | 0 |
| pt→en | 5 | 2.5/4 = 0.6250 | 3.5/4 = 0.8750 | 3.5/4 = 0.8750 | 0/4 | 0/1 | 1/1 | 6 | 5 | 0 |
| en→en | 5 | 3/4 = 0.7500 | 4/4 = 1.0000 | 2.33333/4 = 0.5833 | 0/4 | 1/1 | 0/1 | 9 | 9 | 0 |
| HYP-DEADLOCK | 2 | — (0) | — (0) | — (0) | 0/0 | 1/2 | 1/2 | 0 | 5 | 0 |
| INC-001 | 2 | 1.5/2 = 0.7500 | 1.5/2 = 0.7500 | 1/2 = 0.5000 | 0/2 | 0/0 | 0/0 | 2 | 2 | 0 |
| INC-002 | 2 | 1/2 = 0.5000 | 2/2 = 1.0000 | 2/2 = 1.0000 | 0/2 | 0/0 | 0/0 | 4 | 2 | 0 |
| INC-003 | 4 | 3/4 = 0.7500 | 4/4 = 1.0000 | 2.83333/4 = 0.7083 | 0/4 | 0/0 | 0/0 | 9 | 5 | 0 |

| Consulta | Grupo | Idioma | IDs retornados em ordem | Primeiro relevante @5 | Recall@3 | Recall@5 | Não julgados @5 | Negativos @5 |
|---|---|---|---|---:|---:|---:|---:|---:|
| Q01 | INC-001 | pt-BR | GL-LAT, URL-LAT | 2 | 0.5 | 0.5 | 0 | 1 |
| Q02 | INC-001 | en | GL-LAT, GL-DIAG, URL-LAT, BK-CPU, BK-MEM | 2 | 1.0 | 1.0 | 2 | 1 |
| Q03 | INC-002 | pt-BR | DU-5XX, PO-KCLIENT, BK-CPU, BK-MEM, GL-DIAG | 1 | 0.5 | 1.0 | 2 | 1 |
| Q04 | INC-002 | en | DU-5XX, PO-KCLIENT, BK-MEM, GL-DIAG, DU-CPU | 1 | 0.5 | 1.0 | 2 | 1 |
| Q05 | INC-003 | pt-BR | BK-CPU, PO-CPU, BK-MEM, DU-CPU, GL-GITALY | 1 | 0.5 | 1.0 | 1 | 2 |
| Q06 | INC-003 | pt-BR | BK-MEM, BK-CPU, DU-5XX, GL-DIAG, GL-GITALY | 1 | 1.0 | 1.0 | 3 | 1 |
| Q07 | INC-003 | en | DU-5XX, PO-CPU, BK-CPU, BK-MEM, DU-CPU | 3 | 0.5 | 1.0 | 2 | 1 |
| Q08 | INC-003 | en | PO-MEM, BK-MEM, BK-CPU, DU-5XX, DU-CPU | 2 | 1.0 | 1.0 | 3 | 1 |
| Q09 | HYP-DEADLOCK | pt-BR | abstenção | — | — | — | 0 | 0 |
| Q10 | HYP-DEADLOCK | en | BK-CPU, BK-MEM, DU-5XX, DU-CPU, GL-DIAG | — | — | — | 0 | 5 |

Q01 encontra URL-LAT em segundo lugar e não encontra GL-DIAG no horizonte; GL-LAT é negativo julgado. Q09 abstém por falta de coincidência lexical; Q10 retorna cinco trechos julgados negativos para a mesma necessidade hipotética. Nenhum desses resultados prova ausência ou aplicabilidade fora do corpus. No conjunto, há 15 ocorrências de trechos não julgados nos resultados; elas não são erros nem acertos automaticamente. As proporções por idioma usam apenas quatro positivas e uma ausência por idioma, com consultas pareadas e dependentes; não permitem inferência sobre desempenho por idioma ou generalização.

Durante a implementação houve duas execuções preliminares com ordem de normalização divergente da especificação: a primeira aplicou casefold antes de NFKD; uma correção intermediária omitiu casefold. Foram defeitos de conformidade, não calibração. Corrigida para a ordem congelada, reinstalado o pacote e repetida a avaliação; os resultados finais são os acima, idênticos numericamente aos da primeira execução, sem ajustar a política. Uma primeira verificação mypy também falhou em tipo de fixture de teste e foi corrigida.

## Preparação separada: análise descritiva

Na [STORY-040](decisions/story-040-avaliacao.md), o PO aceitou a conclusão da preparação descritiva. Os [casos](../datasets/hypothesis-evaluation/cases.yaml) e a rubrica não são resultados de inferência nem alteram a avaliação lexical congelada acima.

## STORY-041 — primeiro recorte offline (histórico)

O incremento de 2026-11-07 amplia este recorte; veja a seção seguinte para o estado atual.

A implementação interna `aegisops.descriptive` aceita uma métrica estruturada das quatro já suportadas pelo contrato de incidente e usa um mock em memória. Ela não integra a API. A saída aceita contém observações montadas pelo código e referências conferidas contra os vínculos do contexto; o mock não gera texto. Quando existem exatamente dois sinais da mesma métrica, unidade e agregação em períodos não sobrepostos, a comparação é calculada na ordem temporal. Na pergunta causal sinalizada pelo chamador, relata observações e explicita que não estabelece causa. Não interpreta perguntas abertas, documentos ou as fixtures textuais específicas da avaliação. A string de versão identifica o protocolo de seleção; ainda não há prompt de geração descritiva nem adaptador real para esta análise.

O verificador rejeita a resposta inteira se houver IDs ausentes, duplicados, inexistentes ou fora do contexto, ou campos adicionais, inclusive texto livre. Não há supressão parcial; não há afirmações livres do modelo para avaliar semanticamente. A conferência de IDs não comprova apoio semântico, verdade ou ausência geral de contradição. As comparações determinísticas têm apenas o alcance das regras descritas. Um timeout assíncrono depende da cooperação de cancelamento do provedor; não garante interrupção de uma inferência externa. Limite de 16 sinais e uma chamada mock são limites deste recorte, não autorização de recursos para experimento real.

### Confronto com os casos revisados

Os testes offline exercitam mecanismos relacionados a H-003 (referência inexistente), H-006 (timeout), H-011 (ordem temporal), H-012 (rejeição integral de conteúdo extra), H-019 (ausência de sinais) e H-021 (anotação não enviada), usando entradas e saídas controladas próprias. Não são execução integral dos casos nem revisão semântica de seus estímulos. H-001, H-002, H-004, H-005, H-007–H-010, H-013–H-018 e H-020–H-024 não foram executados como casos da rubrica; observações individuais e documentos em texto livre, perguntas em linguagem natural e adequação à intenção ainda precisam de suporte e avaliação. As fontes, expectativas e grupos permanecem intactos; INC-003 e casos de INC-002 mantêm seus grupos, sem partição independente ou afirmação de representatividade.

Não houve geração bruta de modelo, julgamento de respostas aceitas/exibidas pela rubrica, nem medição de utilidade, abstenção ou rejeição no conjunto dos 24 casos. Essas métricas e a proporção de citações válidas são **não mensuradas**, não 100% ou 0%. A meta exploratória ≥95% na geração bruta continua aplicável apenas a experimento autorizado e não é gate suficiente para produção. Saídas simuladas são testes de implementação, não falhas observadas de modelo ou resultados de inferência. Sem experimento, latência de inferência, tokens e despesas são desconhecidos; zero chamadas reais não comprova custo de uma execução futura. O PO aceitou conjuntamente a STORY-040, sem decisões individuais relatadas por caso.

Alternativas para ampliar a cobertura estão em [story-041-alternativas.md](decisions/story-041-alternativas.md). Qualquer experimento real requer protocolo concreto, ambiente, limites e autorização específica antes da execução.

## STORY-041 — catálogo estruturado e fontes curadas (2026-11-07)

O PO aprovou a alternativa 1 como incremento, sem concluir a história. `aegisops.curated_analysis.analyze_curated` é uma função Python interna e opcional, sem mudança na API HTTP. O chamador seleciona explicitamente IDs de evidência e de até três documentos curados. O contexto da análise contém apenas os IDs escolhidos; a triagem integral continua separada para fallback e pode conter outras observações, portanto um avaliador não deve tratá-la como contexto da resposta. O mock seleciona IDs sem rede. Saída estruturada distingue observações, comparações e orientações; nenhum texto livre do provedor é exibido.

A observação preserva ID do incidente, sinal e evidência, métrica, valor, unidade, período UTC e contagens quando aplicáveis. Esses dados são recebidos pelo núcleo: o vínculo é verificado, mas não há hash externo ou comprovação de verdade da entrada. A comparação é calculada somente para exatamente dois sinais da mesma métrica, unidade e agregação, com períodos ordenáveis não sobrepostos; os IDs dos dois períodos acompanham o resultado. A ausência de comparação não significa igualdade ou ausência de divergência.

Orientações fixas de DU-5XX, BK-CPU e BK-MEM são atribuídas ao documento e não são observações. O carregador existente verifica o corpus inteiro; além disso, cada orientação exige o hash específico da versão curada. A saída informa caminho, hash da unidade, versão do corpus, URL e revisão da fonte. Divergência ou indisponibilidade produz falha controlada, preservando triagem e sem exibir a análise parcial. Os textos são paráfrases curadas locais, não interpretação geral de documentos. Não se executam runbooks ou comandos. O contexto estruturado não informa endpoints ou regiões; a orientação do DU-5XX é condicional. Referência válida não prova apoio semântico geral.

A entrada aceita até 16 sinais, 64 evidências, 16 IDs de evidência e três IDs de documento; IDs têm até 80 caracteres restritos, e há limites para números e agregação. Há uma única chamada de mock com timeout cooperativo; o módulo recebe objeto Python já materializado e não substitui limites de transporte ou isolamento de um provedor real. Falta de seleção, referência fora do contexto, saída extra, falha de corpus, timeout e indisponibilidade têm estados distintos e não mostram conteúdo parcialmente inválido. Para dados de entrada inválidos, vale a exceção do contrato de incidente existente.

### Relação com os 24 casos

A tabela relaciona **mecanismos exercitados**, não resultados completos da rubrica. A solicitação de IDs foi especificada manualmente nos testes; nenhum teste interpreta as perguntas em linguagem natural. Exemplos negativos são respostas controladas ou adaptadas, não inferência de modelo. A rejeição de texto livre resulta do formato permitido, não de detecção semântica automática. O conjunto e os grupos permanecem inalterados.

| Caso | Cobertura deste incremento e pendência |
|---|---|
| H-001 | Comparação p95 e referências testadas; estímulo sem citação e sua classificação semântica não avaliados. |
| H-002 | Múltiplas métricas e rejeição de texto livre exercitadas separadamente; julgamento integral da resposta não implementado. |
| H-003 | Seleção com EVD-001-99 rejeitada no contexto de EVD-001-02. |
| H-004 | Afirmação simulada de deploy rejeitada como texto livre; não há identificação automática de falta de apoio. |
| H-005 | Contexto vazio de incidente válido produz insuficiência; estímulo textual não é interpretado. |
| H-006 | Timeout injetado preserva triagem e omite a análise; não é falha de modelo observada. |
| H-007 | CPU e memória estruturadas e BK-CPU/BK-MEM separados são testados; resposta simulada e intenção não avaliadas integralmente. |
| H-008 | Mesmo mecanismo de H-007; resposta em inglês e adequação linguística não avaliadas. |
| H-009 | Orientação curada distingue CPU e throttling; alegação livre não é classificada semanticamente. |
| H-010 | Orientação DU-5XX atribuída e limitação sobre endpoints/regiões testadas no contexto estruturado; estímulo textual não interpretado. |
| H-011 | Comparação temporal calculada e resposta contraditória adaptada rejeitada por formato; não há detector semântico geral. |
| H-012 | Resposta mista adaptada é rejeitada integralmente; não há avaliação por afirmação nem supressão parcial. |
| H-013 | Não atendido: fixture de fila em texto e pergunta livre não são entradas suportadas. |
| H-014 | Não atendido: fixture de fila e resposta simulada em texto não são interpretadas. |
| H-015 | Não atendido: fixture DNS textual e pergunta livre não são suportadas. |
| H-016 | Não atendido: fixture DNS textual e contradição em texto não são interpretadas. |
| H-017 | Não atendido: sondas em texto, divergência de amostras e pergunta universal não são interpretadas. |
| H-018 | Não atendido: generalização em texto e sondas divergentes não são interpretadas. |
| H-019 | Insuficiência de incidente vazio exercitada; fixture SYN-MISSING-01 e pergunta livre não são entradas suportadas. |
| H-020 | Respostas livres são rejeitadas por formato; fixture SYN-MISSING-01 e classificação semântica não suportadas. |
| H-021 | Anotação maliciosa inserida em incidente estruturado não chega às observações ou orientações; fixture SYN-INJECT-01 e pergunta livre não são suportadas. |
| H-022 | Texto livre é rejeitado por formato; o estímulo e a fixture específicos não foram avaliados integralmente. |
| H-023 | Seleção manual do contexto EVD-002-02/DU-5XX exercita 20%, 200/1000, atribuição, proveniência e limitação; a pergunta livre não foi interpretada. |
| H-024 | Seleção explícita restringe a evidência apresentada; adequação automática à pergunta ou julgamento da resposta simulada não implementados. |

Não há execução integral dos 24 casos, julgamento de qualidade por estágio, resultados de geração ou percentuais para a meta exploratória. Mecanismos testados não demonstram utilidade geral, cobertura semântica, robustez geral a injeção ou representatividade. As variantes de INC-002 e INC-003 continuam em seus grupos; não houve teste independente. Interpretação de perguntas em linguagem natural permanece objetivo futuro, com [alternativas e riscos](decisions/story-041-linguagem-natural.md) separados. Avaliação humana de critérios e evidências é distinta de uma revisão obrigatória por requisição, que não foi introduzida.
