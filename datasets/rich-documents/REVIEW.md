# Revisão do corpus sintético RICH-01 v1.0.0

Estado: **proposta para revisão do PO**, 2026-11-08. A inspeção e os julgamentos abaixo são do agente executor; nenhuma revisão ou aceite humano é alegado. O corpus é pequeno e exploratório, sem suficiência estatística. Não houve teste independente ou cego, nem medição de ingestão ou recuperação.

## Origem, reprodução e limites

Os cinco textos são originais, criados sinteticamente para AegisOps AI pelo agente mediante autorização do PO; os nomes de serviços e ambientes são fictícios. Não foram utilizados documentos privados de terceiros. `documents/` contém os únicos arquivos a fornecer aos futuros mecanismos de ingestão. `questions.yaml` contém somente perguntas e grupos; `judgments.yaml` contém gabaritos, âncoras e justificativas; `manifest.yaml`, `source/`, este arquivo e o gerador não integram o contexto recuperável. Controlar acesso aos gabaritos durante uma avaliação futura; separação de diretórios não constitui controle de segurança.

Fontes YAML e `generate.py` versionados geram os PDFs localmente, sem rede nem LLM. Ferramentas preexistentes: Python 3.14.8, ReportLab 4.4.10 (licença BSD declarada nos metadados instalados), PyYAML 6.0.2 (MIT), Poppler `pdfinfo`/`pdftotext` 25.07.0. Não houve instalação. O modo `invariant=1` fixa metadados internos; a data real de geração fica no manifesto. O gerador exige a versão de ReportLab indicada. A reprodução exata foi verificada nesse ambiente, não garantida em versões ou plataformas diferentes.

```sh
python3 datasets/rich-documents/generate.py
python3 datasets/rich-documents/validate.py --self-test
```

O gerador sobrescreve os PDFs: para comparar sem alterá-los, chamar `generate(source, destino_temporario)` e comparar bytes com o arquivo versionado. Na conferência, os cinco resultados em diretório temporário foram idênticos. SHA-256 do manifesto: `f9a0f97730c9fe7366c0dbcfc3843113565a43b0217ee41367b44e4ef3dd787a`. Hashes dos PDFs abaixo e no manifesto. A ausência vale somente para a versão e hashes aqui indicados, e requer nova conferência se algum documento mudar.

| ID | Característica inspecionada | Páginas | SHA-256 |
|---|---|---:|---|
| RD-01 | Métricas e períodos em texto | 1 | `55097265641d612ec5aaba078f5d46bae6e18a5d9f600a3497d14a91e1e2f493` |
| RD-02 | Associação de células, cabeçalhos e unidades | 1 | `f70e7c04c34cc8a65c2663195098921b4324afaa7c07effc1df982254ecc62a1` |
| RD-03 | Associação por coluna e ordem de leitura | 1 | `52558ff91a447fd3492fec72a46eb1cf6008c4b7c72c43f10dd66b0d6d395322` |
| RD-04 | Contexto de títulos e subseções | 1 | `e9ce8a858af315e82c4a0e2cdf1af0cfec9bae45045cc4a2546941ad11a88f58` |
| RD-05 | Relacionar evidências em páginas distintas | 2 | `90eb2d35e72a68e5cf2dce93c3d66f7e7b1be1615758d1e901c3b36e78c8daff` |

A inspeção visual do executor cobriu todas as seis páginas rasterizadas localmente: tabela com cabeçalhos e duas linhas, colunas lado a lado, títulos/subseções e quebra de página no RD-05. Foram conferidos também os textos dos originais por página, as relações de tabela, os títulos e os períodos. Para Q12 e Q13, o executor examinou o conteúdo completo dos cinco PDFs: não há limite de deadlock do Atlas nem endereço IP do Lume. Isso é revisão do executor, não aprovação humana nem prova automatizada de ausência semântica.

O validador abre os PDFs via Poppler, confere limites, arquivos, hashes, páginas, versões, IDs, seções e âncoras, incluindo células em uma mesma linha física e relações de grupo. O teste de mutação rejeita hash, ID repetido, página, âncora, grupo, ausência sem justificativa, linha de tabela e PDF ausente. Encontrar texto e coordenadas não prova que uma resposta seja sustentada ou que um PDF tenha o layout correto; essas conclusões exigem leitura e revisão visual. A tabela de evidências a seguir permite ao PO conferir o original, inclusive relações e ausência.

## Julgamentos propostos para revisão humana

Todos os itens permanecem `pending`. Recomendação do executor: aceitar o julgamento proposto após conferência humana do documento e das relações indicadas; a recomendação não representa aceite.

| ID e pergunta | Resposta esperada | Documento e página | Justificativa e âncoras para revisão | Recomendação |
|---|---|---|---|---|
| Q01: Qual foi a latência p95 do Atlas entre 10:00 e 10:20 UTC? | 840 ms | RD-01 p. 1 | 1. Latência do Atlas: “Durante 10:00–10:20 UTC, a latência p95 do Atlas foi 840 ms.” | Conferir e aceitar se correto |
| Q02: Qual era o p95 do Atlas na janela anterior? | 310 ms | RD-01 p. 1 | 1. Latência do Atlas: “Na janela anterior de 09:40–10:00 UTC, o p95 foi 310 ms.” | Conferir e aceitar se correto |
| Q03: Com qual frequência o runbook recomenda verificar a latência? | A cada 5 minutos | RD-01 p. 1 | 1. Latência do Atlas: “O runbook recomenda verificar a latência a cada 5 minutos.” | Conferir e aceitar se correto |
| Q04: Qual o limite de alerta da fila Vega, em mensagens? | 120 mensagens | RD-02 p. 1 | 1. Limites das filas: “Vega /  120 mensagens /  8 minutos”; cruzar linha Vega com coluna Limite de alerta, unidade mensagens | Conferir e aceitar se correto |
| Q05: Qual a idade máxima da fila Lyra, em minutos? | 15 minutos | RD-02 p. 1 | 1. Limites das filas: “Lyra /  75 mensagens /  15 minutos”; cruzar linha Lyra com coluna Idade máxima, unidade minutos | Conferir e aceitar se correto |
| Q06: O que verificar após aumento de HTTP 503 no serviço Íris? | O pool de conexões | RD-03 p. 1 | 1. Diagnóstico por serviço: “Para Íris, aumento de HTTP 503”; 1. Diagnóstico por serviço: “indica verificar o pool de conexões.” | Conferir e aceitar se correto |
| Q07: O que verificar após aumento de HTTP 429 no serviço Lume? | O limite de requisições | RD-03 p. 1 | 1. Diagnóstico por serviço: “Para Lume, aumento de HTTP 429”; 1. Diagnóstico por serviço: “indica verificar o limite de requisições.” | Conferir e aceitar se correto |
| Q08: Qual condição de CPU aciona a investigação de processos ativos? | CPU acima de 90% por 10 minutos | RD-04 p. 1 | 1. Diagnóstico de recursos > 1.1 CPU: “Se a CPU permanecer acima de 90% por 10 minutos, investigar processos ativos.” | Conferir e aceitar se correto |
| Q09: Qual condição de memória aciona a investigação de consumo por processo? | Memória livre abaixo de 12% por 5 minutos | RD-04 p. 1 | 1. Diagnóstico de recursos > 1.2 Memória: “Se a memória livre ficar abaixo de 12% por 5 minutos, investigar consumo por processo.” | Conferir e aceitar se correto |
| Q10: No cenário em que a mensagem mais antiga atingiu 18 minutos, qual comparação é indicada? | Comparar a taxa de entrada com a taxa de processamento | RD-05 p. 1, RD-05 p. 2 | 1. Sinal da fila Órion: “No cenário OR-7, a idade da mensagem mais antiga atingiu 18 minutos.”; 2. Ação para OR-7: “Para o cenário OR-7, comparar a taxa de entrada com a taxa de processamento.” | Conferir e aceitar se correto |
| Q11: Qual janela deve ser usada para registrar as duas taxas associadas ao cenário OR-7? | A mesma janela de 10 minutos | RD-05 p. 2 | 2. Ação para OR-7: “Para o cenário OR-7, comparar a taxa de entrada com a taxa de processamento.”; 2. Ação para OR-7: “Registrar ambas as taxas na mesma janela de 10 minutos.” | Conferir e aceitar se correto |
| Q12: Qual é o limite de deadlock do serviço Atlas? | Sem resposta no corpus | Todos: RD-01 a RD-05, p. 1–2 conforme documento | Não consta em nenhum dos cinco PDFs v1.0.0; conferência humana integral pendente. | Conferir e aceitar se correto |
| Q13: Qual é o endereço IP do serviço Lume? | Sem resposta no corpus | Todos: RD-01 a RD-05, p. 1–2 conforme documento | Não consta em nenhum dos cinco PDFs v1.0.0; conferência humana integral pendente. | Conferir e aceitar se correto |

## Agrupamento e próximas dependências

Os grupos `atlas`, `filas`, `http`, `recursos`, `orion` e `ausencias` mantêm variantes relacionadas juntas; o grupo de ausências é conservador. Não há partições de desenvolvimento e avaliação: a amostra é pequena e já foi exposta ao executor. Antes de qualquer avaliação, congelar versões, manifesto, grupos e política de acesso; caso haja partição, manter documentos, cenários e variantes no mesmo grupo e justificar sua independência. Nenhum conteúdo não julgado deve ser convertido automaticamente em negativo.

Para concluir STORY-061 o PO deve revisar os cinco documentos, a tabela, as 13 perguntas e seus gabaritos, as duas ausências, a política de grupos, os critérios e limites; registrar explicitamente o alcance do aceite e resolver eventuais observações. STORY-062 depende de STORY-061 `done` após esse gate, de contrato próprio refinado e de autorização específica. O protocolo de avaliação e a seleção de ferramentas para 062 permanecem pendentes; não foram executados OCR, extração comparativa, chunking experimental, recuperação, embeddings ou inferência.
