# STORY-062 — protocolo congelado antes da extração

Data: 2026-11-11. Autoridade: execução local autorizada pelo PO nesta atividade; RICH-01 v1.0.0 aceito em [story-061-aceite](../../doc/decisions/story-061-aceite.md). Esta rubrica foi escrita antes de executar os extratores. Nenhuma revisão humana posterior é presumida. Atualizar o protocolo após observar saídas invalida a comparação; correção exigiria outra versão e relato explícito.

## Entradas e configurações

Verificar hashes aprovados do manifesto, perguntas, gabaritos e cinco PDFs; somente o diretório de PDFs é montado no extrator. Nenhuma fonte de geração, pergunta ou gabarito é montada no sandbox. Salvar e calcular hash das saídas de cada extrator antes de disponibilizá-las ao chunking ou ao avaliador. Q12 e Q13 não entram nos denominadores de positivas ou em teste de ausência.

- `poppler`: `pdftotext -enc UTF-8 -eol unix -f N -l N /input/RD-NN.pdf -` por página. `poppler_layout` usa as mesmas opções com `-layout`, apenas diagnóstico.
- `pdfplumber`: versão e dependências locais documentadas; `page.extract_text(x_tolerance=3, y_tolerance=3, layout=False)`, linhas e caixas nativas por `extract_text_lines()`; tabelas por `find_tables()` com padrões da versão instalada. Texto, caixas, posições e células são saída da ferramenta. Títulos e hierarquia não são nativos, não inventar relações. A ordem dos blocos é a fornecida pela biblioteca, não uma garantia de ordem semântica.
- Janelas fixas: 600 caracteres Unicode, passo 500, reinício por página; última janela termina no fim do texto. Offsets zero-based, intervalo semiaberto na saída textual da página; registrar apenas a sobreposição real.
- Estrutural em pdfplumber: linhas extraídas nativamente e alinhadas sem perdas à saída textual, agrupadas em ordem por página até 600 caracteres; linhas identificadas na mesma tabela pelo bbox ficam juntas quando couberem. Não inferir títulos; caso alinhamento ou limites sejam inviáveis, registrar falha, não fabricar blocos. Fragmentos de linha maior que 600 são cortados deterministicamente, com perda potencial registrada. Sem sobreposição ou junção de páginas. Sem estrutura nativa em Poppler textual, célula estrutural inviável.
- Limites: um núcleo por afinidade e quota 100%, cgroup memory.max 1073741824 bytes, prazo 30 s por documento/configuração, tmpfs total 104857600 bytes, 1 MiB de texto por documento e 200 chunks por documento. Cada processamento roda em namespace de rede separado; somente loopback isolado, sem interfaces externas. Um aquecimento e três repetições por documento/configuração quando viável; manter resultados individuais. Nenhum processamento continua após falha de verificação do isolamento.

## Rubrica imutável de relações (denominadores)

Julgar no resultado todo de cada página. Para chunks, julgar tanto cada chunk individual quanto a união dos chunks de uma pergunta. Tratar todos os itens não processados como não julgados e expor o denominador total e o efetivamente julgado. Verificações lexicais automáticas são indícios, não avaliação semântica.

| ID | Documento original | Relação que precisa sobreviver |
|---|---|---|
| OR-01 | RD-03, p. 1, coluna esquerda | Na ordem da coluna: serviço Íris → aumento de HTTP 503 → verificar pool de conexões; os três itens devem continuar associados ao Íris. |
| OR-02 | RD-03, p. 1, coluna direita | Na ordem da coluna: serviço Lume → aumento de HTTP 429 → verificar limite de requisições; os três itens devem continuar associados ao Lume. |
| OR-03 | RD-03, p. 1 | Ordem de leitura completa por coluna: terminar a informação da coluna Íris antes de iniciar a coluna Lume. Intercalação horizontal é perda de ordem, mesmo com as palavras presentes. |
| HI-01 | RD-04, p. 1 | `1. Diagnóstico de recursos` → `1.1 CPU` → CPU acima de 90% por 10 minutos → investigar processos ativos. |
| HI-02 | RD-04, p. 1 | `1. Diagnóstico de recursos` → `1.2 Memória` → memória livre abaixo de 12% por 5 minutos → investigar consumo por processo. |
| HI-03 | RD-04, p. 1 | `2. Orientações` → `2.1 Registro` → registrar janela antes de hipóteses; não associar a subseções do diagnóstico. |
| TB-01 | RD-02, p. 1 | Cabeçalho `Fila` × linha `Vega` × coluna `Limite de alerta` = `120 mensagens`. |
| TB-02 | RD-02, p. 1 | Cabeçalho `Fila` × linha `Lyra` × coluna `Idade máxima` = `15 minutos`. |

OR-01/02 são duas associações; OR-03 é uma avaliação distinta da ordem de leitura. HI-01/02/03 são três relações; TB-01/02 são duas relações. Em tabelas sem estrutura nativa, fazer julgamento textual separado da preservação de relação estruturada; não imputar sucesso estrutural por presença de palavras. Para títulos, distinguir sequenciamento textual, relação estrutural nativa e inferência; ausência de metadados de seção não significa seção correta.

## Gabaritos e métricas

Após congelar saídas e chunks, o avaliador pode ler julgamentos aprovados: 15 ocorrências pergunta-âncora / 11 positivas; 4 positivas multiâncora (Q06, Q07, Q10, Q11), sem eliminar âncoras repetidas entre perguntas. Marcar preservada somente quando contexto, valor e relação necessários estão presentes. Para tabelas, avaliar linha, coluna, cabeçalho e unidade; Q10 exige duas páginas. Registrar individualmente todas as decisões com evidência, avaliador e justificativa. A pontuação por palavra é indicador automático sujeito à revisão semântica pelo executor. Reportar cobertura de âncoras, cobertura de perguntas por união e por chunk único, relações TB, OR e HI, proveniência por página/seção, duplicações, truncamentos e falhas; informar todos os denominadores. Não avaliar ranking ou retrieval.

Execução local isolada em bolha de montagem somente leitura, `/tmp` e `/dev/shm` limitados em conjunto a 100 MiB; apenas PDFs, código necessário e bibliotecas são montados. cgroup do systemd para processo e filhos; limites de rede, memória, CPU, tempo e volume devem ser verificados antes de qualquer PDF. Medir tempo de parede e CPU e pico de memória agregados por execução com `memory.peak` e `cpu.stat`, separando aquecimento, extração e chunking; inicialização incluída no tempo do processo e também marcada dentro do worker quando mensurável. Sem queda silenciosa, downloads ou armazenamento compartilhado entre fases.
