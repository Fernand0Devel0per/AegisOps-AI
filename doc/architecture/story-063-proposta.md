# Proposta para revisão — STORY-063: recuperação e citações

Estado em 2026-11-12: **proposta para decisão, não autorização para executar**. [STORY-063](../../roadmap/stories/STORY-063.yaml) permanece backlog, [SPEC-063](../../agents/specs/SPEC-063.yaml) draft e [ACT-063](../../agents/activities/ACT-063.yaml) pending. A [STORY-062 foi aceita](../decisions/story-062-aceite.md) para fins exploratórios; este documento não contém implementação, ranking, métricas obtidas ou adoção.

## Objetivo, referência e comparações

Medir recuperação lexical e qualidade de referências sobre o RICH-01 v1.0.0, mantendo o corpus, perguntas e julgamentos aceitos. Preparar uma linha de base do pipeline **histórico, imutável** e uma possível melhoria experimental em artefatos separados:

| Célula proposta | Dados de entrada | Papel e limite |
|---|---|---|
| B1 — baseline | Poppler textual + chunks fixos congelados na STORY-062 | Referência simples para o novo corpus, sem alterar seus arquivos. |
| C1 — candidata | pdfplumber + chunks fixos congelados na STORY-062 | Mesmas consultas, ranking, k e orçamento; o chunk histórico contém texto, não os metadados nativos de tabela. |
| D1 — diagnóstico condicionado | Poppler `-layout` | A saída histórica não tem chunks fixos para esta configuração; sua criação e avaliação exigem autorização e configuração própria. Espaços visuais não são tabela estruturada. |
| E1 — melhoria condicionada | Cópia versionada dos dados de extração com metadados nativos transportados aos chunks | Célula nova, separada e identificada; não reescreve B1/C1, não altera resultados da STORY-062 nem implica adoção. Requer autorização para implementação e rubrica apropriada. |

Comparar B1 e C1 informa diferença entre **pipelines de extração**, mantendo ranking e regra de chunking iguais; não atribuir diferença a chunking isoladamente. E1 altera a representação e deve ser comparada com C1 no mesmo texto, mesma extração, mesmas fronteiras e orçamento, mostrando separadamente custo de metadados. B1 e C1 têm seis chunks cada, um por página; isso não demonstra diferença entre chunking fixo e estrutural. Alternativas de tamanho ou fronteiras em corpus maior exigem plano e autorização próprios.

## Tabelas, proveniência e ambiguidade

1. **Histórico:** avaliar apenas o conteúdo e metadados presentes nos chunks existentes. A tabela nativa do pdfplumber está na extração e não chegou aos chunks; não atribuir metadados de célula ao chunk retroativamente.
2. **Sidecar candidato:** preservar, em registro de proveniência separado por chunk, ID e hash do PDF, página, origem e offsets na extração, bbox da tabela, índices de linha/coluna, texto de cabeçalhos, valores e unidades; versionar e congelar mapeamento antes de avaliar. Fazer o ranking sobre o mesmo texto que C1; medir se as citações resolvem os metadados efetivamente transportados. Cabeçalho, linha, valor, coluna e unidade precisam ser conjuntamente verificáveis, com campos desconhecidos explícitos.
3. **Texto enriquecido candidato:** outro experimento possível converter cabeçalhos e células extraídos em texto associado ao chunk, distinguindo texto original de contexto gerado e contabilizando-o no orçamento. Esse texto pode mudar termos e ranking, portanto é uma configuração diferente de C1/sidecar. Se aprovado, fixar transformação e confrontar com original antes da medição.

Metadados de seção são opcionais: somente registrar caminho hierárquico quando sustentado por evidência localizável; caso contrário `ausente` ou `não julgado`. Registrar se cada relação é extração nativa, inferência, anotação humana ou desconhecida. Para as duas colunas RD-03, preservar posições e ordem quando disponíveis; sinal e orientação sem associação inequívoca permanecem ambíguos, sem reconstrução presumida. `-layout` pode apoiar revisão visual, mas não gera semântica nativa. Não converter conteúdo não julgado em negativo.

Citar documento e hash/versão, página e intervalos exatos do chunk ou âncora; seção e célula apenas quando a fonte da relação permitir confirmá-las. Checar separadamente referência resolvível e suporte semântico da afirmação. Para Q10, conservar duas âncoras e páginas distintas, ligadas pelo cenário OR-7: relatar cobertura parcial e união dos chunks; não exigir que ambas caibam em um único chunk quando a configuração respeitar páginas.

## Ranking lexical e equivalência ao baseline C1

O [baseline da STORY-031](../EVALUATION.md) é limitado ao corpus Markdown C1, com integridade verificada; ele não aceita PDF ou chunks arbitrários. Propor **adaptador isolado** para unidades locais, sem modificar `src/aegisops/retrieval.py`, seu corpus, hashes ou bypass de verificações. Reproduzir NFKD, remoção de marcas Unicode, casefold, sequências alfanuméricas, conjunto de termos distintos, score por interseção, somente score positivo, ordenação por score decrescente e ID ascendente, k inteiro 1–5 e abstenção sem coincidência. Preservar as mesmas regras de entrada e erros, inclusive consulta inválida e falha técnica.

Antes de medir RICH-01, validar equivalência no C1 com os mesmos trechos verificados, consultas, k, IDs, scores, ordenação, empate e estados; incluir testes de normalização Unicode, entrada inválida, k, ausência, empates e hash divergente. Registrar qualquer divergência como bloqueio da afirmação de equivalência. Congelar versões, regras e hashes do adaptador e das entradas. As medidas C1 publicadas não são baseline numérico comparável aos PDFs e não devem ser tratadas como ganho.

## Métricas propostas e orçamento

Sujeito à aprovação, fixar k=3 e k=5, mantendo o mesmo ranking e a mesma unidade de julgamento para B1/C1. O universo de referência são as âncoras das 11 consultas positivas da STORY-061: 15 **ocorrências pergunta-âncora**, inclusive trechos compartilhados entre perguntas. Uma âncora conta coberta somente quando a evidência retornada e seu contexto sustentam a relação julgada; presença de palavras, mesma página ou ID resolvível não bastam. Falhas e itens não julgados permanecem separados.

- **Recall@k por pergunta:** âncoras relevantes distintas da pergunta, semanticamente cobertas no top k, divididas pelo total de âncoras relevantes julgadas daquela pergunta; publicar cada fração, soma e média sobre positivas. Não reduzir denominador porque um extrator perdeu a âncora; perda conhecida é parte do resultado, salvo falha técnica ou item não julgável reportado separadamente.
- **MRR@k:** recíproco do primeiro rank que contenha ao menos uma âncora relevante com contexto suficiente; zero se nenhuma for recuperada. Média por pergunta com soma e n. Primeiro trecho parcialmente relevante não comprova resposta completa: reportar separadamente fração de perguntas com todas as âncoras e relações cobertas pela união, inclusive Q10, e cobertura parcial das perguntas multiâncora.
- **Citações:** referências resolvíveis / referências emitidas e afirmações sustentadas / afirmações julgadas, com inspeção semântica, numeradores, denominadores e não julgados. Sem gerador autorizado, avaliar apenas as referências dos trechos e as afirmações de gabarito examinadas; não alegar qualidade de respostas geradas.
- **Q12/Q13:** ausência é relativa aos cinco PDFs e hashes aprovados, não um negativo por trecho. Reportar consultas com algum retorno e abstenções / 2, e abstenções em positivas / 11, com saídas individuais. Um retorno em consulta sem resposta não é automaticamente uma resposta falsa: o trecho pode conter contexto relacionado; eventual afirmação sem apoio exige julgamento próprio. Uma abstenção lexical significa ausência de coincidência, não prova de ausência semântica. Não tratar falha de provedor, corpus ou processamento como abstenção.

Proposta de dois cortes simultâneos: reportar métricas no top k **antes** do limite de contexto e após limitar a 1.800 caracteres Unicode, na ordem do ranking. Contar todo texto/contexto e metadados efetivamente enviados; não contar apenas o trecho útil. Se um chunk ultrapassar o saldo, truncar no limite restante e registrar intervalo, truncamento e âncoras efetivamente completas; parar ao esgotar o orçamento. Mesmo limite, unidade, k e política em todas as células. Documentar a representação e o custo dos metadados para não dar vantagem gratuita à célula enriquecida. O orçamento e a política são propostas, não requisitos aprovados.

## Separação, ausência de independência e recursos

Os futuros mecanismos recebem somente chunks/documentos, configuração e texto da consulta; não recebem `judgments.yaml`, respostas, âncoras, justificativas ou este relatório como contexto recuperável. O avaliador lê rótulos somente após congelar ranking e saídas. Separar fisicamente acessos e registrar hashes; isolamento lógico sozinho não prova controle de acesso.

O corpus e as perguntas já foram expostos durante a construção e a STORY-062; a análise será exploratória, não cega ou independente. Q12 depende de Atlas, Q13 de Lume e ambas são julgadas sobre o corpus completo. Antes de qualquer particionamento futuro, revisar o grafo de dependências entre documentos, cenários, variantes e ausências; manter dependentes juntos ou criar e revisar novo conjunto independente. Mudanças de documento, hash ou gabarito exigem versão e avaliação do efeito no aceite. Não atribuir representatividade estatística à amostra de 13 perguntas.

Propor execução local em CPU, sem rede, OCR, inferência, serviços pagos ou alteração de infraestrutura, com controles verificáveis e limites a serem aprovados. Definir antes de executar: tempo por consulta e indexação, memória agregada, tamanho do corpus/saída, repetições, isolamento e método de medição de tempo de parede, CPU e pico de memória, incluindo filhos. Publicar resultados individuais, ambiente, numeradores, denominadores, falhas e exclusões; não presumir que os limites da STORY-062 foram automaticamente aprovados para esta etapa.

## Decisões necessárias antes de executar

O PO precisa autorizar a STORY-063 e os limites; escolher B1/C1 e a inclusão de D1; decidir se E1 ou texto enriquecido serão construídos e com qual rubrica; aprovar k, orçamento, tratamento de truncamento, avaliação de citações e política de ausências/grupos; aprovar dependências ou modelos se propostos. Nova dependência estrutural, integração à API, mudança de arquitetura ou custo operacional relevante exige decisão apropriada e ADR quando aplicável antes da implementação. Docling, embeddings, vetores, inferência real e serviços externos não foram autorizados por esta proposta.

Após autorização, trabalhar na branch `feat/story-063`, refinar história, SPEC-063 e ACT-063 e congelar configurações antes de observar rankings. Gerar relatório de resultados e handoff somente após execução, mantendo STORY-060 e EPIC-006 abertos até seus gates próprios.
