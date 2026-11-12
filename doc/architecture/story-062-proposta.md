# Proposta para revisão — STORY-062: extração e chunking

Estado histórico em 2026-11-08: **proposta, não autorização de execução**. Em 2026-11-11, o PO autorizou a execução local e os [resultados estão em revisão](rich-document-ingestion-results.md). A [STORY-062](../../roadmap/stories/STORY-062.yaml) estava em backlog, SPEC-062 em draft e ACT-062 pending na data da proposta. A [STORY-061](../../roadmap/stories/STORY-061.yaml) foi concluída após [aceite do PO](../decisions/story-061-aceite.md). Este documento não registra experimento, resultado, instalação ou decisão de arquitetura. A decisão posterior e os parâmetros efetivos estão no protocolo congelado e nos resultados.

## Objetivo e entradas

Comparar a preservação das informações dos PDFs e dos chunks com o original aprovado, sem medir retrieval. Usar exclusivamente RICH-01 v1.0.0: cinco PDFs, seis páginas, 11 perguntas positivas, 15 ocorrências de âncoras e duas perguntas sem resposta. Âncoras repetidas em perguntas diferentes são contadas como ocorrências pergunta-âncora, não como trechos únicos. Q06, Q07, Q10 e Q11 precisam de mais de uma âncora. Congelar hashes de manifesto, PDFs, perguntas e gabaritos antes de iniciar; [aceite](../decisions/story-061-aceite.md) identifica os arquivos.

Separar os PDFs e as saídas de extração do processo de julgamento: apenas `documents/` é entrada do extrator; perguntas, respostas, âncoras e fontes de geração não são alimentadas ao extrator nem incluídas nos chunks. O avaliador pode acessar o gabarito somente para medir as saídas, após elas serem gravadas; registrar política e hashes. Tratar documento como dado não confiável, sem executar instruções embutidas. Não alterar os PDFs ou gabaritos aceitos.

## Alternativas de extração

| Alternativa | Papel na proposta | Condições e limites |
|---|---|---|
| Poppler `pdftotext`, modo texto, uma página por chamada | Referência textual simples, usando ferramenta já presente no ambiente da STORY-061. | Fixar versão, opções, encoding e tratamento de falhas. A presença anterior não autoriza automaticamente a execução do estudo. Não presumir preservação de ordem, tabela ou hierarquia. |
| Um extrator estruturado local, a escolher após análise | Candidato para produzir texto com estrutura de tabela, títulos, ordem e páginas, quando suportados. | Comparar opções como Docling e ferramentas PDF locais mais leves; especificar versão, licença, dependências transitivas, necessidade de modelos/download, uso offline e requisitos reais antes de propor instalação. Se não houver alternativa autorizada e viável, registrar célula inviável e não declarar AC-02 da comparação estrutural concluído. |
| `pdftotext -layout` | Diagnóstico opcional de ordem/colunas, não substituto presumido para extração estruturada de tabelas ou hierarquia. | Somente se autorizado e com configuração registrada; não chamar espaços preservados de tabela estruturada sem verificar relações. |

Recomendação: autorizar primeiro uma comparação local do modo textual com **um** candidato estruturado leve após comprovação de licença, dependências e isolamento. Docling é candidato, não escolha nem instalação aprovada; ferramentas que exijam download, inferência ou recursos acima dos limites precisam de decisão específica. O estudo não adota nenhuma delas na arquitetura.

## Chunking proposto

Comparar as duas regras abaixo sobre **a mesma saída de cada extrator**. Uma regra adicional de tamanho só após justificativa e autorização; não confundir mudança de extrator com mudança de regra.

1. **Tamanho fixo:** 600 caracteres Unicode por chunk, sobreposição de 100, em ordem determinística; iniciar novamente em cada página. O último chunk pode ser menor. Registrar offsets na saída extraída e página; não fazer OCR.
2. **Estrutura:** percorrer a estrutura fornecida pelo extrator, mantendo título/caminho e parágrafos ou linhas de tabela associados; agrupar unidades consecutivas até 600 caracteres, sem sobreposição e sem ultrapassar página. Dividir unidade maior deterministicamente em janelas de 600 caracteres, sinalizando perda de contexto. O título herdado precisa ter origem identificada, ser incluído no limite de 600 e ser marcado como contexto adicionado; não fabricar seção nem tabela quando a estrutura estiver ausente. Para extrator que não expõe estrutura utilizável, marcar célula inviável, sem rotular heurística como estrutura verdadeira.

Esses valores são proposta de experimento, não decisão ou resultado. Comparar também o efeito de páginas separadas: Q10 não deve ser considerada íntegra em um único chunk se suas duas evidências estiverem em páginas distintas; avaliar cobertura em conjunto e registrar se partes individuais mantêm contexto suficiente. Reportar tamanho efetivo, quantidade de chunks, sobreposição e fronteiras, sem realizar ranking ou recuperação.

## Matriz e julgamentos

Para cada extrator autorizado, congelar saída por documento antes de aplicar cada regra de chunking. A matriz planejada é extrator textual e extrator estruturado × regras fixa e estrutural; registrar célula inviável em vez de omiti-la. Julgar extração antes de chunking para distinguir perda inicial de perda introduzida depois. Não usar diferenças de extrator como prova do efeito do chunking.

- **Extração:** ocorrências pergunta-âncora preservadas / 15; perguntas positivas com todas as âncoras e relações preservadas / 11; reportar por documento, inclusive falhas e não julgados. Presença de palavras não é suficiente: conferir valor, unidade, contexto e relação no original.
- **Tabela:** relações de célula julgadas corretas / 2 (Q04 e Q05), cada uma com cabeçalho, linha, coluna e unidade. Relatar também se o método só preservou texto sem estrutura confiável.
- **Ordem e hierarquia:** definir antes da execução uma lista explícita, exaustiva e revisável de relações a julgar a partir de RD-03 e RD-04; publicar numeradores, denominadores e não julgados. Não inventar denominadores antecipadamente.
- **Chunks:** ocorrências pergunta-âncora preservadas em pelo menos um chunk / 15 e perguntas com todas as âncoras e suas relações preservadas no conjunto de chunks / 11. Separadamente, perguntas cuja evidência completa cabe em um chunk / 11 e os quatro casos com múltiplas âncoras; verificar contexto, duplicação, fronteira, ordem, páginas e seções.
- **Proveniência:** referências de página corretas / referências produzidas e referências de seção corretas / referências produzidas, indicando ausentes e não julgadas. Uma referência que existe não prova suporte semântico. Falha técnica e documento não processado não são abstenção, negativo ou sucesso.
- Q12/Q13 são ausências aprovadas no corpus completo, não referências positivas de extração. Usá-las para retrieval ou abstenção pertence a STORY-063 e exige novo contrato/autorização.

Avaliação humana e verificações automáticas devem ser identificadas separadamente; registrar resultados individuais, falhas, casos não processados, denominadores totais e julgados, ambiente e incerteza. Os 15 vínculos incluem ocorrências repetidas, não 15 evidências únicas. Nenhuma conclusão estatística ou superioridade geral será derivada desta amostra.

## Recursos e segurança propostos para autorização

- Local, CPU apenas; sem GPU, OCR, inferência, serviços pagos, rede ou download. Exigir mecanismo de isolamento de rede comprovável antes da execução; se não existir, suspender configurações que não possam ser isoladas.
- Até 10 páginas e 5 MiB por PDF; 1 CPU e teto agregado de 1 GiB para processo e filhos, com mecanismo de controle que realmente inclua subprocessos. Sem controle verificável, registrar a limitação e não afirmar que o teto foi aplicado.
- Até 30 segundos de parede por documento/configuração e 100 MiB de temporários no total; até 200 chunks e 1 MiB de texto extraído por documento/configuração. Cancelar processo e filhos ao exceder limite e registrar falha; não truncar silenciosamente. Confirmar ferramenta de medição e enforcement antes de executar.
- Medir tempo de parede, CPU e pico de memória agregados por execução de extração, incluindo filhos; identificar SO, hardware, versões, ferramenta, unidades, aquecimento e política de cache. Propor três repetições por extrator/documento após uma execução de aquecimento registrada; limites aplicam-se a cada repetição. Medir chunking separadamente com seu tempo e memória e guardar resultados individuais. Se os limites não puderem ser impostos/medidos com confiança, reduzir escopo ou solicitar decisão, sem reportar medidas fictícias.

## Vazamento, autorização e saída

Não há partição independente no corpus aceito. Q12 se relaciona a Atlas e Q13 a Lume, além de ambas dependerem da ausência no corpus completo. Uma divisão futura exige analisar o grafo de cenários, documentos e negativas, mantendo dependências juntas ou produzindo corpus e julgamentos independentes com revisão própria; simples troca do campo de grupo não resolve. Qualquer mudança de gabaritos, documentos ou hashes exige versão e avaliação de impacto sobre o aceite.

Antes da execução, o PO deve decidir: autorização da STORY-062 e limites acima; escolha dos candidatos e eventual instalação/dependências ou necessidade de ADR; método de isolamento e medição; parâmetros de chunking e rubrica de ordem/hierarquia; tratamento das células inviáveis. Após autorização, refinar STORY-062, SPEC-062 e ACT-062 na branch própria e congelar o protocolo. Saída prevista: `doc/architecture/rich-document-ingestion-results.md`, configurações e dados reproduzíveis, testes pertinentes e handoff. STORY-063, recuperação, embeddings, API e Colibri permanecem fora desta proposta.
