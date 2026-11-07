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

## Preparação separada: hipóteses ampliadas

Na [STORY-040](decisions/story-040-avaliacao.md), o PO aprovou direção experimental condicional; os [casos ampliados](../datasets/hypothesis-evaluation/cases.yaml) e a rubrica refinada aguardam revisão. Não são resultados de inferência nem alteram a avaliação lexical congelada acima.
