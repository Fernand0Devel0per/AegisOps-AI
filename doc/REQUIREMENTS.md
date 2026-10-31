# Requisitos para a primeira triagem

## Estado e escopo

Requisitos da [STORY-003](../roadmap/stories/STORY-003.yaml), aceitos pelo PO em 2026-10-30 para a primeira vertical; a descoberta foi aceita pelo PO após revisão documentada na STORY-004. Os limiares abaixo são escolhas **sintéticas para testes**, não medições nem recomendações operacionais. Não há motor, API ou integração implementados. Os critérios foram aceitos como proposta sintética; a aceitação não transforma os valores em regras de produção. Ela respeita o papel determinístico e o fallback do [ADR-0002](adr/0002-llm-local-primeira-vertical.md).

## Entrada e restrições

A entrada é um incidente sintético local com ID, serviço fictício, ambiente sintético, janela UTC, sinais e evidências. Os três arquivos da [STORY-002](INCIDENTS.md) são exemplos. Para este recorte, a janela do incidente tem exatamente 10 minutos; cada sinal tem período de exatamente 5 minutos, inteiramente contido na janela, com início inclusivo e fim exclusivo. Podem existir períodos sucessivos ou sobrepostos. Apenas os sinais da entrada são usados; não consultar infraestrutura, rede, runbooks nem fonte externa durante a investigação. Não executar remediação nem registrar dados pessoais ou credenciais.

Cada sinal contém ID único no incidente, métrica reconhecida, valor numérico finito, unidade, período, agregação e origem. P95 representa duração das requisições; CPU e memória são utilização média em relação, respectivamente, à capacidade de CPU alocada e ao limite de memória do serviço. As taxas 5xx incluem numerador e denominador inteiros de respostas para o período: denominador positivo, numerador entre zero e denominador e valor igual a 100 × numerador / denominador, com tolerância absoluta de 0,000001 ponto percentual. Percentuais ficam entre 0 e 100; latência não é negativa. Os nomes e unidades aceitos são os da tabela abaixo; outros sinais são entrada inválida neste recorte.

Cada evidência tem ID único no incidente e aponta para um sinal existente no mesmo incidente. Cada sinal tem ao menos uma evidência; cada evidência aponta a um único sinal. IDs de incidente, sinal e evidência não podem se repetir entre si dentro da entrada. IDs e demais campos obrigatórios devem ser textos não vazios; os intervalos devem ser timestamps UTC válidos. Não se pressupõe que uma referência válida comprove a verdade ou o suporte semântico de uma afirmação.

## Classificação sintética proposta

Para **cada sinal** presente na janela, a tabela fornece um nível; o resultado é o maior nível observado, na ordem `normal < media < alta`. O menor limite de cada faixa é inclusivo e o maior é exclusivo. Não se calcula variação percentual nem se exige um valor de referência anterior. Cada valor de p95 já é agregado em seu período e nunca deve ser combinado por média de percentis. As linhas são independentes: não há regra de causalidade nem regra especial para sinais simultâneos.

| Métrica | Unidade | `normal` | `media` | `alta` |
|---|---|---:|---:|---:|
| `http_request_duration_p95` | ms | < 500 | ≥ 500 e < 1500 | ≥ 1500 |
| `http_5xx_rate` | percent | < 5 | ≥ 5 e < 10 | ≥ 10 |
| `cpu_utilization` | percent | < 95 | ≥ 95 e < 99 | ≥ 99 |
| `memory_utilization` | percent | < 90 | ≥ 90 e < 95 | ≥ 95 |

A leitura das fixtures produz:

| Cenário | Derivação por sinal | Resultado e evidências |
|---|---|---|
| [INC-001](../datasets/incidents/inc-001-latencia.json) | 120 ms → normal; 900 ms → media; 0,5% 5xx → normal | `media`; EVD-001-01, EVD-001-02, EVD-001-03 |
| [INC-002](../datasets/incidents/inc-002-erros-5xx.json) | 1% 5xx → normal; 20% → alta; 92% CPU → normal | `alta`; EVD-002-01, EVD-002-02, EVD-002-03 |
| [INC-003](../datasets/incidents/inc-003-saturacao.json) | 60% memória → normal; 97% memória → alta; 95% CPU → media | `alta`; EVD-003-01, EVD-003-02, EVD-003-03 |

Os resultados coincidem com os rótulos propostos e aprovados como exemplos na STORY-002. Para esta tabela específica, 92% de CPU é `normal`: esse nome descreve apenas a faixa sintética, não a saúde real do serviço. Os rótulos propostos não afirmam ausência de impacto nem causa. Para o resultado básico, apresentar uma observação por sinal e citar a evidência de ID lexicograficamente menor vinculada a ele; incluir também o nível de cada sinal e a severidade máxima. Assim, havendo múltiplas evidências para um sinal, a seleção é determinística. Nos três arquivos cada sinal tem exatamente uma.

## Dados ausentes e inválidos

Entrada estruturalmente válida sem nenhum sinal e sem evidências produz `insuficiente`, sem severidade `normal/media/alta`, com observações vazias e limitação de ausência de sinais. Uma entrada com um ou mais sinais válidos pode ser classificada pela tabela; a saída lista nominalmente cada uma das quatro métricas ausentes como limitação. Ausência de qualquer métrica não é preenchida com zero e uma classificação parcial não demonstra ausência de degradação.

ID repetido, sinal sem evidência, evidência órfã, unidade ou métrica não reconhecida, janela ou período inválido, valor fora do intervalo ou taxa inconsistente torna a entrada inteira `entrada_invalida`; retornar detalhes dos campos inválidos, sem severidade, observações ou explicação. Na presença de violações e ausência de sinais, prevalece `entrada_invalida`. Ausência de evidência para sinal presente é erro de integridade; ausência de todos os sinais **e** evidências é insuficiência. O contrato de transporte e os formatos de erro serão definidos nas histórias aplicáveis, não aqui.

## Saída, explicação e fallback

A saída lógica básica contém ID do incidente, estado (`classificado`, `insuficiente` ou `entrada_invalida`), severidade quando classificável, observações com valor, unidade, período, nível e IDs de evidência, limitações e estado da explicação. Ela distingue hipótese de observação; neste recorte hipóteses não são geradas. Não afirmar causa raiz nem emitir recomendação de alteração de infraestrutura. Referências de cada observação devem resolver para a evidência associada ao sinal de origem.

Para `classificado`, o núcleo determinístico disponibiliza um conjunto de frases canônicas produzidas a partir das observações e da severidade; cada frase tem ID e evidências associadas. O conjunto inclui uma frase de severidade máxima com referência a pelo menos um sinal que a determina. O LLM local pode selecionar e ordenar esses IDs para formar a explicação. O verificador independente exige resposta estruturada, IDs de frases existentes, sem duplicatas, a frase de severidade máxima obrigatória e referências resolvíveis para os sinais que as frases descrevem. O texto exibido é montado exclusivamente a partir das frases canônicas, sem texto livre retornado pelo modelo. Assim o modelo não determina severidade nem introduz novas afirmações. Essa restrição conservadora foi aceita pelo PO para a primeira vertical e continua sujeita à avaliação de utilidade; referência válida isoladamente não prova suporte semântico.

Na falha, indisponibilidade, resposta malformada ou rejeição da explicação, preservar exatamente o resultado básico determinístico e seus IDs de evidência; assinalar explicação indisponível/rejeitada e a limitação, sem apresentar o texto rejeitado. Para `insuficiente` ou `entrada_invalida`, não solicitar explicação ao LLM. Tempo máximo, protocolo, modelo e mensagem específica permanecem decisões posteriores; o tratamento de qualquer expiração é a mesma falha com fallback. A política não exige usar o LLM para verificar sua própria saída.

## Critérios observáveis propostos

1. **CT-01:** INC-001 produz `classificado`, `media` e as três referências indicadas na tabela.
2. **CT-02:** INC-002 produz `classificado`, `alta` e as três referências indicadas na tabela.
3. **CT-03:** INC-003 produz `classificado`, `alta` e as três referências indicadas na tabela.
4. **CT-04:** Para cada métrica, valores exatamente nos dois limites entram, respectivamente, em `media` e `alta`; valores imediatamente menores entram na faixa anterior, respeitado o domínio de cada unidade.
5. **CT-05:** Entre vários sinais válidos da janela, a severidade é a máxima da tabela e as observações citam evidência resolvível de cada sinal.
6. **CT-06:** Uma entrada válida sem sinais nem evidências resulta em `insuficiente`; métricas ausentes numa entrada classificável constam nas limitações.
7. **CT-07:** Uma entrada inconsistente resulta em `entrada_invalida` sem severidade ou explicação.
8. **CT-08:** Uma seleção válida do LLM usa apenas frases e referências predefinidas; falha ou seleção inválida preserva a saída básica e sinaliza indisponibilidade ou rejeição.
9. **CT-09:** Observações não são hipóteses e nenhum resultado declara causa raiz; não há remediação.

## Casos de falha propostos

| Caso | Resultado observável |
|---|---|
| Sem sinais nem evidências, demais metadados válidos | `insuficiente`, sem severidade nem explicação, com limitação explícita. |
| 5xx com denominador zero ou taxa incompatível com contagens | `entrada_invalida`, campo identificado, sem severidade nem explicação. |
| Sinal sem evidência ou evidência apontando a sinal inexistente | `entrada_invalida`; não apresentar observação como confiável. |
| Valor fora do domínio, unidade divergente ou período fora da janela | `entrada_invalida`; não substituir por zero nem inferir unidade. |
| LLM indisponível, expirado, resposta malformada ou frase/referência inexistente | Resultado básico preservado; explicação não exibida e falha ou rejeição sinalizada. |

## Pendências e validação humana

O PO aceitou os limiares sintéticos, a política de informação parcial e a explicação restrita em 2026-10-30; o registro de Q-002 e Q-003 está em [questões abertas](decisions/open-questions.md). O PO informou ter feito a revisão independente e aceitou a descoberta; o ajuste de registro do fluxo está documentado na STORY-004. Uma implementação futura deve testar fronteiras, entradas inválidas e saídas rejeitadas, inclusive suporte das frases canônicas, sem alegar que uma checagem de referência resolve toda a avaliação semântica.
