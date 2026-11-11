# STORY-062 — resultados exploratórios de extração e chunking

Estado em 2026-11-11: execução local concluída e **em revisão do PO**. Julgamentos semânticos abaixo são autorrevisão do executor, não aceite humano. O experimento não compara recuperação ou qualidade de respostas geradas e não adota ferramentas no produto.

## Referência e método

Corpus RICH-01 v1.0.0 aprovado: cinco PDFs, seis páginas, 11 perguntas positivas e 15 ocorrências pergunta-âncora; Q12/Q13 não integram esses denominadores. Manifesto, documentos, perguntas e gabaritos foram conferidos contra os hashes de [aceite](../decisions/story-061-aceite.md) antes e depois do processamento. Apenas o diretório `documents/` foi montado no extrator. O [protocolo](../../datasets/rich-document-experiment/protocol.md), inclusive OR-01–03, HI-01–03 e TB-01–02, foi congelado no commit local `2a4cdb6` antes da primeira extração.

Poppler 25.07.0 foi executado em UTF-8, com `-eol unix` e uma chamada por página; `-layout` é diagnóstico separado. `pdfplumber` 0.11.10 e dependências já disponíveis foram usados sem instalação; licenças, versões, requisitos aplicáveis, hashes do código e ressalvas em [inventário](../../datasets/rich-document-experiment/output/dependency-inventory.json). A compatibilidade de versões dos requisitos locais foi conferida; não se fez auditoria jurídica integral das licenças transitivas nem adoção no produto.

Foram congeladas as [saídas de extração](../../datasets/rich-document-experiment/output/extraction-freeze.json) antes do chunking e os [chunks](../../datasets/rich-document-experiment/output/chunk-freeze.json) antes do julgamento. [Revisão por caso](../../datasets/rich-document-experiment/semantic-review.yaml), [métricas](../../datasets/rich-document-experiment/output/evaluation.json), [saídas](../../datasets/rich-document-experiment/output/extractions/) e [chunks](../../datasets/rich-document-experiment/output/chunks/) são rastreáveis. Procurar palavras é apenas indicador automatizado; os estados de preservação abaixo são julgamento manual do executor sobre contexto e relações. A sequência de comandos e critérios está no protocolo; `evaluate.py` confere hashes antes de abrir o gabarito. `run.py` grava em `output/` e pode sobrescrever os resultados: para reproduzir, use uma cópia isolada da árvore e compare hashes e limitações do ambiente.

## Preservação por extrator

| Configuração | Ocorrências preservadas / 15 | Perguntas com evidência e relação preservadas / 11 | Tabela textual TB / 2 | Tabela nativa TB / 2 |
|---|---:|---:|---:|---:|
| Poppler textual | 11 | 7 | 0 | 0 |
| pdfplumber | 13 | 9 | 2 | 2 |
| Poppler `-layout`, diagnóstico | Não agregado como configuração principal | Não agregado | 2 | 0 |

Todos os documentos foram processados nas três extrações; nenhum caso foi excluído ou considerado não julgado. Os 15 são **ocorrências por pergunta**, não 15 trechos únicos. As células TB exigem cabeçalho, linha, coluna, valor e unidade. No Poppler textual, as palavras existem, mas a ausência de fronteiras de linha/célula não demonstra de maneira verificável a associação de coluna; por isso Q04 e Q05 não contam como preservadas. O `pdfplumber` forneceu tabela nativa com `Fila`, `Limite de alerta`, `Idade máxima`, `Vega / 120 mensagens / 8 minutos` e `Lyra / 75 mensagens / 15 minutos` em RD-02 p. 1. `-layout` mantém as linhas visualmente alinhadas, sem criar metadados semânticos de tabela.

Q06 e Q07 não contam como integralmente preservadas pelos dois extratores principais. Em RD-03 p. 1, ambos intercalam os sinais das duas colunas antes das orientações; as palavras estão presentes, mas a associação da orientação com o serviço é ambígua na representação salva. O pdfplumber gerou caixas de **linhas completas**, não as coordenadas individuais de cada trecho dessa linha nesta execução. O diagnóstico `-layout` preservou espaçamento suficiente para inspecionar visualmente as associações OR-01 e OR-02, mas continua lendo por linhas intercaladas: OR-03 falha. Assim, OR-01/02/03 são 0/3 nos dois extratores principais e 2/3 no diagnóstico, conforme a rubrica; isso não estabelece hierarquia nativa.

RD-04 p. 1 mantém as três relações HI-01–03 em sequência textual nos três modos, 3/3 por leitura do executor. Nenhuma configuração gerou metadados nativos de hierarquia ou referências de seção: 0 referências de seção produzidas, portanto correção de referências produzidas é **não aplicável (0/0)**, e cobertura de seção é 0/6 páginas. A biblioteca disponibiliza elementos posicionados, mas este pipeline não infere títulos/subseções; a sequência textual não prova hierarquia semântica nativa. Referências de página são corretas em 6/6 páginas processadas por extrator.

Q10 conserva o sinal de OR-7 na p. 1 e a ação na p. 2 de RD-05; a associação entre páginas depende da identificação comum do cenário. Não houve truncamento observado nos cinco PDFs nem omissão técnica de páginas. Repetições preservaram saídas idênticas; diferenças de ordem e ausência de estrutura são perdas de representação, não falhas de execução.

## Efeito do chunking

| Combinação | Ocorrências / 15 | Evidências completas na união / 11 | Em um único chunk / 11 | Chunks | Sobreposição efetiva |
|---|---:|---:|---:|---:|---:|
| Poppler textual + fixo | 11 | 7 | 6 | 6 | 0 caracteres |
| Poppler textual + estrutural | — | — | — | — | Inviável: a saída não fornece unidades estruturais nativas. |
| pdfplumber + fixo | 13 | 9 | 8 | 6 | 0 caracteres |
| pdfplumber + estrutural por linhas/tabela | 13 | 9 | 8 | 6 | 0 caracteres |

Cada página tem menos de 600 caracteres e gerou um chunk integral; as estratégias fixa e estrutural produziram os mesmos trechos para o `pdfplumber`. Os quatro casos multiâncora são Q06, Q07, Q10 e Q11: as relações de Q06/Q07 já estavam ambíguas na extração; Q10 é suficiente pela união de páginas, mas não por um único chunk; Q11 cabe na p. 2. No Poppler, Q04/Q05 também já haviam perdido a relação de tabela. **Nenhuma perda adicional por fronteira de tamanho foi observada**, e o conjunto não testa o efeito prático de sobreposição de 100 caracteres. O caso concreto de contexto indisponível em um único chunk é Q10, por respeitar o limite de página, não por truncamento.

O chunk estrutural agrupou as linhas da tabela que cabem juntas, mas os chunks finais contêm texto e offsets, não as células/bboxes nativos: a estrutura de tabela nativa está na extração e não é propagada como metadado de chunk. A seção também não é fabricada: `section: null` e `section_status: not_extracted`. A relação TB textual continua legível nos chunks do pdfplumber, mas TB como metadado estruturado é 0/2 nos chunks. Os offsets são semiabertos na saída da página e foram testados contra o texto original congelado.

## Recursos, isolamento e falhas

[Preflight](../../datasets/rich-document-experiment/output/preflight.json) demonstrou namespace de rede diferente do host, somente loopback isolado e falha de conexão ao loopback do host; não há interface externa. `bubblewrap` montou somente PDFs, código e bibliotecas necessários em leitura; raiz e `/dev` ficaram somente leitura. Os tmpfs de `/tmp` e `/dev/shm` somam exatamente 100 MiB. Cada processo e seus filhos rodaram em cgroup systemd com `memory.max=1073741824`, `cpu.max=100000 100000`, afinidade a um núcleo e prazo de 30 s. Foi aplicado limite de 1 MiB de texto/documento e 200 chunks/documento. Em cada configuração/documento houve um aquecimento e três medições; o maior tempo acumulado observado dessas quatro execuções foi 0,421 s. Sem GPU, OCR, inferência, rede, modelos ou serviços pagos.

Ambiente: Fedora Linux 43, kernel 7.2.13-100.fc43 x86_64, glibc 2.42, Intel Core i5-1235U, 12 CPUs lógicas visíveis e afinidade ao núcleo lógico 0; Python 3.14.8 e bubblewrap 0.12.0. Frequência e cache não foram controlados. Detalhes em [ambiente](../../datasets/rich-document-experiment/output/environment.json) e [máquina](../../datasets/rich-document-experiment/output/machine-info.json).

A tabela usa média de 15 execuções medidas por configuração (cinco documentos × três), e maior `memory.peak` agregado de processo e filhos. Tempo de parede começa no supervisor após criação do escopo e inclui inicialização do sandbox, carregamento e operação; CPU é a diferença de `cpu.stat`. A operação interna é medida no worker, separadamente de chunking. Inicialização parcial dentro do worker e dados individuais, incluindo aquecimentos, estão em [measurements.json](../../datasets/rich-document-experiment/output/measurements.json); a diferença entre parede e operação inclui inicialização, serialização e overhead, não uma medida pura de startup. Memória é pico do cgroup incluindo supervisor e não um pico exclusivo do extrator.

| Configuração | Parede média (s) | CPU média (s) | Operação interna média (s) | Pico agregado máximo (MiB) |
|---|---:|---:|---:|---:|
| Extração Poppler | 0,0408 | 0,0400 | 0,0100 | 16,54 |
| Extração Poppler `-layout` | 0,0408 | 0,0397 | 0,0098 | 16,79 |
| Extração pdfplumber | 0,1035 | 0,1021 | 0,0600 | 26,22 |
| Chunk Poppler fixo | 0,0239 | 0,0231 | 0,000006 | 12,88 |
| Chunk pdfplumber fixo | 0,0239 | 0,0230 | 0,000005 | 13,05 |
| Chunk pdfplumber estrutural | 0,0237 | 0,0230 | 0,000026 | 12,77 |

São medições locais muito curtas, sujeitas a cache e overhead, não previsão de desempenho. Todas as 120 execuções da rodada final — aquecimento e três repetições de 15 pares extrator/documento e 15 pares chunker/documento — terminaram sem erro ou limite excedido; a configuração Poppler estrutural foi registrada como inviável. A primeira rodada foi preservada em [output-attempt-01](../../datasets/rich-document-experiment/output-attempt-01/): após descobrir que o algoritmo não agrupava explicitamente todas as linhas de uma tabela antes de testar o limite, o agrupamento foi corrigido e a matriz repetida, sem alterar rubrica ou extratores. Uma segunda rodada foi guardada em [output-attempt-02](../../datasets/rich-document-experiment/output-attempt-02/); após ajustes de estilo e qualidade do código, a matriz foi repetida com as versões finais dos scripts. Os hashes de todas as extrações e chunks das três rodadas são idênticos neste corpus pequeno. Um teste sintético inicialmente falhou porque o tamanho escolhido não excedia 600 caracteres; foi corrigido para exercitar a fronteira e passou. Um lint inicial também apontou problemas de estilo; foram corrigidos antes da terceira rodada. Esses registros não são falhas de extração do corpus. Os [testes de falha](../../datasets/rich-document-experiment/output/failure-probes.json) executaram uma saída sintética 7 e um processo sintético que excedeu 30 s: ambos foram classificados como falha e timeout, respectivamente.

## Interpretação e próximos passos

Neste recorte, `pdfplumber` preservou mais relações avaliadas devido à tabela nativa, ao custo observado de maior tempo e memória. O Poppler textual é mais simples e barato, mas perdeu estrutura de tabela; `-layout` é diagnóstico útil para associação visual das colunas. Nenhum dos dois demonstrou leitura completa por coluna ou hierarquia nativa. Como os chunks foram idênticos por página e a estrutura nativa da tabela não foi transportada para eles, **não há evidência aqui para escolher chunking estrutural como superior**. Uma comparação futura deve incluir documentos mais longos e uma representação que mantenha metadados de tabela, com versão e revisão próprias.

Como candidatos à STORY-063, preservar Poppler textual + fixo como referência e pdfplumber + fixo para examinar o valor de suas saídas, sem presumir que os metadados perdidos cheguem ao mecanismo de recuperação. Antes de executar a STORY-063, definir e aprovar como transportar estrutura, revisar grupos/ausências e política de avaliação, adaptar e validar o baseline lexical C1 conforme o protocolo e obter autorização específica. Nenhuma partição independente ou teste cego é alegado; corpus sintético pequeno e já exposto impede generalização.
