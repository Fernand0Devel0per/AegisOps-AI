# Protocolo inicial proposto — documentos ricos

Estado histórico: preparação em 2026-11-07, quando nenhum PDF ou julgamento havia sido produzido. Em 2026-11-08, STORY-061 gerou [corpus e julgamentos](../../datasets/rich-documents/REVIEW.md) posteriormente [aceitos pelo PO](../decisions/story-061-aceite.md) para exploração, sem executar comparações ou recuperação. Este protocolo deve ser refinado e congelado antes da execução e revisto quando os dados forem materializados. A execução dos incrementos requer autorização específica do PO. A primeira vertical, API e Colibri não mudam. Os documentos são dados não confiáveis; nunca executar seus comandos nem tratá-los como instruções.

## Situação e baseline

[STORY-031](../../roadmap/stories/STORY-031.yaml) implementa `retrieve` sobre 11 trechos Markdown fixos e íntegros: tokens alfanuméricos distintos após NFKD, remoção de marcas e casefold; score é a contagem de termos distintos em comum, empate por ID, k de 1 a 5, retorno apenas de score positivo e abstenção sem coincidência. O carregador é limitado ao corpus C1 empacotado e verificado por hash; não recebe PDFs nem chunks arbitrários. Não há leitura de PDFs ou RAG completo na API. A recuperação e a análise curada são componentes internos separados, sem integração da rota; a máquina de estados STORY-050 é protótipo não adotado.

[Resultados C1](../../doc/EVALUATION.md) usam 10 consultas exploratórias, 8 positivas e 2 ausências: Recall@3 5,5/8, Recall@5 7,5/8 e MRR@5 5,83333/8; 1/2 retornos em ausência e zero falhas técnicas. São medidas apenas daquele corpus, não baseline numérico dos futuros PDFs. O conjunto não tem teste independente, contém grupos dependentes e não julgados. [Julgamentos](../../datasets/evaluation/queries.yaml), [revisão](../../datasets/evaluation/REVIEW.md) e [resultados](../../datasets/evaluation/results-c1-lexical.json) são fontes históricas, não rótulos dos novos documentos.

Para novos documentos, preparar adaptador isolado que reproduza precisamente tokenização, score, ordenação, corte e abstenção do algoritmo atual, comparando seus resultados com `retrieve` em C1 antes de qualquer medição. O adaptador não deve modificar `src/` ou contornar a verificação do corpus existente; registrar divergências e não chamá-lo equivalente enquanto não forem resolvidas. O ranking é o baseline transferido; seu corpus, extração e unidades mudam e devem ser declarados. Reconhecer custos distintos dos pipelines. Não comparar diretamente os números de C1 com os do corpus novo como ganho.

## A — corpus proposto: STORY-061

Na proposta original de 2026-11-07, os exemplos abaixo eram apenas um plano de criação de documentos sintéticos ou autorizados. Os documentos efetivamente produzidos, versões e hashes estão no [manifesto](../../datasets/rich-documents/manifest.yaml) e no [aceite](../decisions/story-061-aceite.md). Usar páginas numeradas e uma referência humana independente do texto extraído, com coordenadas/trechos por página quando úteis.

| Família proposta | Pergunta ilustrativa | Referência a criar e julgar |
|---|---|---|
| PDF textual simples | Qual intervalo de verificação é indicado para o serviço fictício Atlas? | Valor explícito em página e seção identificadas. |
| PDF com tabela | Qual limite de alerta corresponde à fila fictícia Vega? | Linha, cabeçalho, coluna e página; manter a relação valor/unidade. |
| PDF em duas colunas | Qual observação distingue as filas Vega e Lyra? | Trecho por coluna/página; evitar concatenação que troque o sentido. |
| Títulos e seções hierárquicas | Qual condição pertence à subseção de diagnóstico de saturação? | Caminho hierárquico e página. |
| Informação em páginas diferentes | Qual ação de investigação corresponde ao sinal descrito na página anterior? | Duas evidências separadas, páginas e relação esperada. |
| Visual, condicionado | Que tendência o gráfico apresenta? | Somente se houver gabarito de dados, localização e rubrica de julgamento visual independente; caso contrário excluir e explicar. |
| Sem resposta | Qual é o limite de deadlock do serviço fictício? | Após examinar todo o corpus, ausência relativa à versão congelada; não inventar resposta. |

Cada pergunta requer ID, grupo, formulação, resposta esperada ou marca de ausência, documentos e versões, páginas/seções de cada evidência, critério e justificativa de relevância e negativos julgados quando disponíveis. Não julgados não viram negativos. Fontes, documentos e variantes do mesmo cenário ficam no mesmo grupo; congelar partições de desenvolvimento e avaliação por grupo antes de ajustes, com hashes e políticas de acesso. Se número ou independência não permitirem divisão significativa, declarar estudo exploratório e não teste independente ou cego. Revisão do PO sobre corpus, rótulos, ausências e protocolo é exigida na STORY-061; registrar o alcance exato da revisão, sem presumir concordância individual.

## B — extração e chunking: STORY-062

Congelar corpus, versão de ferramentas e configurações antes de medir. No mínimo avaliar extração textual simples e, quando autorizada, extração com preservação de estrutura; combinar cada extração disponível com chunking por tamanho e por estrutura, quando viável. Fixar unidade e tamanho em tokens ou caracteres, sobreposição, ordem, regras de fronteira, títulos herdados, metadados e limites; registrar valores reais sem inventá-los agora. Usar tabela de configurações para células inviáveis, motivo e consequência. Não confundir mudança de extrator com mudança de chunking.

Comparar com gabarito humano por documento: evidências preservadas/total; células e relações de tabela corretas/avaliadas; títulos, hierarquia, ordem de leitura e vínculos de página/seção corretos/avaliados; contexto necessário mantido/total; perdas, truncamento, duplicação, falhas e documentos não processados. Registrar denominadores, exclusões e exemplos localizáveis. Documentos em colunas podem embaralhar a ordem; tabelas podem perder cabeçalhos, unidades e relações; quebras podem separar evidências; gráficos, imagens, fontes, codificação e texto em imagens podem desaparecer; OCR pode introduzir erros. Não declarar suporte visual por mera extração textual.

Medir tempo de parede por documento e configuração, pico de memória e CPU de processo/filhos com ferramenta e unidade explicitadas, versões, hardware, SO, ambiente, aquecimento, repetições e dispersão. Separar inicialização, extração e indexação; registrar falhas e limites de tamanho, tempo e recursos antes de executar. Valores de limites e método de isolamento serão propostos para aprovação antes do experimento. Sem rede ou execução do conteúdo.

## C — recuperação e comparação: STORY-063

Matriz mínima: mesmo corpus/extração e chunks fixos, baseline lexical reproduzido; depois mesmo extrator e julgamentos variando tamanho; depois mesmo extrator variando chunk fixo/estrutural. Comparar extratores separadamente em desenho fatorial viável. Busca vetorial é candidata somente com justificativa, autorização específica, licença, recursos e decisão apropriada; congelar modelo, versão, parâmetros e índice se aprovada. Não é necessário banco vetorial.

Julgar sobre **âncoras de evidência no documento original**, não IDs de chunks: mapear cada chunk para páginas, seções e spans; uma âncora é coberta somente quando o trecho contém informação suficiente, não por mera interseção de página. Para perguntas com múltiplas âncoras, reportar cobertura parcial e proporção de perguntas com todas as âncoras recuperadas. Mapear antecipadamente os trechos candidatos para não trocar a unidade de julgamento entre configurações; contabilizar trechos não mapeáveis e não julgados. Comparar o mesmo k, política de corte, consultas e versões; fixar também orçamento de contexto (caracteres ou tokens) para impedir vantagem automática por chunks maiores, registrando os dois cortes e truncamentos. Mudanças de corpus, extração ou julgamentos exigem estratos separados e não permitem atribuição isolada ao retrieval.

Por consulta positiva: Recall@k = âncoras relevantes distintas cobertas no top k / âncoras relevantes julgadas; MRR@k = 1/rank do primeiro trecho relevante, ou zero se não houver. Agregar médias por consulta com soma e n, reportar por grupo e configuração. Precisão@k só se os trechos no denominador tiverem julgamento apropriado; mostrar não julgados e o denominador efetivo, sem imputar negativos. Reportar cobertura parcial e integral, citações resolvíveis/citações exibidas e citações que sustentam a afirmação/citações revisadas, com método humano e casos não julgados; referência válida não garante apoio semântico. Sem gerador não afirmar qualidade de resposta: avaliar citações dos trechos e, se aplicável, afirmações de gabarito, discriminadas.

Para ausências: retornos indevidos e abstenções corretas / ausências julgadas, e abstenções indevidas / positivas; falhas técnicas separadas de abstenções e ausências. Medir latência de consulta, CPU e pico de memória, indexação separada, tamanho e repetição, ambiente e percentis somente quando tamanho justificar; publicar dados individuais, numeradores, denominadores, falhas, exclusões e incertezas. Congelar parâmetros antes da avaliação e manter dados de avaliação fora do ajuste. Amostras pequenas são exploratórias, sem alegar superioridade generalizável ou causalidade entre estratégias.

## Alternativas para decisão posterior

| Candidata | Vantagem pretendida | Limite e condição |
|---|---|---|
| Texto simples + chunk fixo + ranking atual | Simplicidade e referência local | Pode perder ordem, hierarquia e tabelas; extrator PDF ainda não escolhido nem instalado. |
| Extração estruturada, por exemplo Docling | Preservar seções e tabelas | Compatibilidade, licença, recursos, isolamento e ganhos são desconhecidos aqui; instalação/adoção estrutural exigem decisão e autorização. |
| Chunking por estrutura | Reter títulos e contexto | Tamanhos desiguais e estrutura extraída incorreta podem enviesar comparação; testar com orçamento comum. |
| Vetores em memória | Candidato para relações sem correspondência literal | Embeddings/modelos podem custar recursos e exigir execução real; dependência/modelo e autorização ainda não definidos. |
| FAISS ou PostgreSQL/pgvector | Candidatos para indexação ou persistência se necessidade demonstrada | Dependências operacionais e persistência não justificadas pelo estudo atual; ADR e aprovação prévios, não requisitos. |

Questões para o PO: autorizar cada execução e recursos; revisar corpus e rótulos; escolher se uma ferramenta candidata pode ser instalada/testada após análise de compatibilidade e ADR quando aplicável; autorizar separadamente modelos reais, se propostos; avaliar resultados e eventual decisão arquitetural. Nenhuma decisão de adoção está sendo tomada agora.
