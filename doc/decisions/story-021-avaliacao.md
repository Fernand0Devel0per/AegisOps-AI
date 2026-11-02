# Avaliação preliminar da explicação — STORY-021

Estado: fatia independente avaliada antes de integrar qualquer modelo ou endpoint. Não é avaliação da qualidade de um LLM e não conclui AC-04. A especificação está em rascunho e a proposta de integração aguarda decisão em [ADR-0006](../adr/0006-proposta-integracao-colibri.md).

## Política avaliada

A saída básica vem de `triage_incident`; um catálogo de frases é gerado de seus valores, métricas, períodos, níveis e evidências, sem texto livre de entrada. `S-MAX` refere-se ao primeiro sinal no nível máximo; cada observação tem frase própria. Uma seleção deve ser um objeto contendo exclusivamente `sentence_ids`: IDs existentes, únicos, com `S-MAX`. O verificador confere o catálogo calculado, os IDs e vínculos de evidência a sinal na entrada validada; a saída é a sequência de objetos canônicos selecionados, sem texto adicional. Esse módulo ainda não solicita LLM nem monta resposta HTTP.

## Casos e resultados controlados

A suíte [test_explanation.py](../../tests/unit/test_explanation.py) executada antes da integração confronta os máximos das três fixtures com valores e IDs esperados, e verifica ordem de uma seleção válida. Rejeita objeto malformado, IDs inexistentes ou duplicados, ausência da frase máxima, texto livre com afirmação sem apoio, catálogo adulterado com alegação causal, evidência inexistente ou ligada a outro sinal e evidência removida da fonte e divergência entre observação e sinal. Uma entrada válida sem sinais não gera catálogo de explicação. A suíte completa passou com 116 testes em 1,94 s; isso inclui 18 testes novos, não 116 casos independentes de avaliação de modelo.

Estes são testes sintéticos e sobretudo de conformidade e segurança do mecanismo; os três exemplos máximos e um período são comparados a expectativas explícitas, não há medição representativa de utilidade ou análise semântica exaustiva de cada frase. Referências resolúveis não provam que afirmações sejam verdadeiras no mundo real. Uma afirmação não apoiada não é representável como texto retornado pelo modelo sob esta política; o teste de adulteração avalia proteção do catálogo, não capacidade de o verificador julgar texto livre arbitrário.

## Antes da integração

Após decisão do PO, avaliar o candidato real e a configuração aprovada com as três fixtures, resposta estruturada completa, IDs inexistentes/duplicados, alegações livres, dados insuficientes e falhas; registrar entradas, versões, critério, resultados, tempo e limites sem inventar métricas. Validar licença e gerenciamento de tempo, memória e processo. Se o modelo não produzir seleção válida ou o isolamento não for adequado, não concluir a integração e voltar ao PO. O experimento de [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml) foi exploratório e não cumpre esta avaliação.

## Comparação experimental de 256 e 512 tokens — 2026-11-01

O PO solicitou comparar os dois tetos de saída com timeout de até 5 minutos. As duas execuções abaixo usam INC-001, o mesmo prompt em **uma única linha**, o catálogo gerado pelo código, Colibri commit `e0db083cdc9e563e0766cc6fc661ef23c32298e0`, OLMoE-1B-7B-0125-Instruct convertido para int8, execução CPU, `--ram 5`, `--ctx 2048`, `--temp 0` e `--ngen` variando entre 256 e 512. Foram sequenciais, um processo por chamada, iniciados com `systemd-run --user --scope`, `MemoryMax=7G`, `MemorySwapMax=1G`, `CPUQuota=400%` e `/usr/bin/timeout --kill-after=5s 300`; `/usr/bin/time` registrou tempo decorrido e pico RSS. Os pesos e logs locais ficam fora do repositório. O contexto de 2048 é parâmetro experimental, não decisão aprovada para integração.

Prompt integral, enviado como uma única mensagem:

```text
Selecione e ordene IDs das frases abaixo para explicar o incidente. Inclua obrigatoriamente S-MAX. Retorne somente um objeto JSON com a chave sentence_ids e uma lista de IDs, sem texto extra e sem IDs repetidos. S-MAX: Severidade máxima media, determinada pelo sinal 2. S-001: Sinal 1: http_request_duration_p95 = 120 ms, de 2026-10-01T10:00:00+00:00 até 2026-10-01T10:05:00+00:00 (fim exclusivo); nível normal. S-002: Sinal 2: http_request_duration_p95 = 900 ms, de 2026-10-01T10:05:00+00:00 até 2026-10-01T10:10:00+00:00 (fim exclusivo); nível media. S-003: Sinal 3: http_5xx_rate = 0.5 percent, de 2026-10-01T10:05:00+00:00 até 2026-10-01T10:10:00+00:00 (fim exclusivo); nível normal.
```

| Teto de saída | Tempo decorrido | Pico RSS reportado | Código de saída | Resultado |
|---|---:|---:|---:|---|
| 256 tokens | 49,83 s | 3.583.760 KiB | 0 | Rejeitado |
| 512 tokens | 51,72 s | 3.584.152 KiB | 0 | Rejeitado |

As duas respostas foram idênticas; o texto retornado pelo modelo incluiu a cerca Markdown aqui representada e o seguinte conteúdo:

````text
```json
{
  "sentence_ids": [
    "S-001",
    "S-002",
    "S-003"
  ],
  "ids": [
    "S-001",
    "S-002",
    "S-003"
  ]
}
```
````

A resposta integral não é JSON válido por causa da cerca. Para diagnóstico apenas, retirar a cerca permite analisar o objeto: o verificador o rejeitou por conter a chave extra `ids`; mesmo sem ela, falta `S-MAX`. Não foi exibida uma explicação como se tivesse sido aprovada. O resultado básico da fixture continua `classificado`, severidade `media`, com as três observações e IDs EVD-001-01/02/03; fallback pela API ainda não está implementado.

A saída parece completa sintaticamente dentro da cerca, mas a CLI não registrou contagem de tokens gerados nem motivo de parada; não se pode concluir que algum teto foi atingido, nem estimar desempenho ou custo geral. Uma execução por teto, com temperatura zero e o mesmo prompt, não demonstra confiabilidade nem diferença estatística. O timeout vale por execução; a execução em servidor HTTP, cancelamento efetivo no servidor, concorrência e limite total de memória em outros ambientes não foram testados. A licença e os demais cenários permanecem pendentes.

Uma tentativa preliminar com quebras de linha no prompt foi interrompida: a CLI tratou as linhas como mensagens distintas. Seus resultados não integram a tabela. A comparação válida não demonstra que aumentar o teto por si só corrige a obediência ao formato ou a omissão da frase obrigatória. Avaliar alternativas de prompt e suporte a saída estruturada antes de decidir a integração; não relaxar o verificador para apresentar conteúdo não verificado.

## Comparação Qwen3-Coder — concluída com limites

Em 2026-11-01 o PO autorizou baixar e testar Qwen3-Coder-30B-A3B convertido para int4 para Colibri. A preparação usa [repositório do modelo convertido](https://huggingface.co/Justvugg/Qwen3-Coder-30B-A3B-colibri-int4), revisão `d839110a17d31b4e6fa9f3d973b751f779b6b9c6`, 49 arquivos de pesos e licença declarada Apache-2.0. A documentação do Colibri indica `--cap 32` como controle de cache desse motor, que não usa o parâmetro `--ram`. O código do Colibri está no commit `e0db083cdc9e563e0766cc6fc661ef23c32298e0` em cópia local isolada; `make qwen36` concluiu. Os pesos ficam fora do Git, em `~/.local/share/aegisops-models/qwen3-coder-30b-a3b-int4`.

Download e testes foram encadeados em um serviço transitório local `aegisops-story021-qwen-eval.service`; o download foi concluído e os dois testes terminaram com código 0. Para consultar o estado real, usar `systemctl --user status aegisops-story021-qwen-eval.service` e ler `.local/story021-qwen-experiment/status.json`; arquivos nessa pasta são locais e ignorados pelo Git. A tarefa verifica a conclusão do download fixado antes de executar cada inferência com a mesma entrada INC-001 e o mesmo prompt da comparação anterior. Os dois tetos são 256 e 512 tokens, cada qual limitado a 300 segundos, processo em `MemoryMax=9G`, `MemorySwapMax=1G`, `CPUQuota=400%`, `--cap 32`, contexto 2048 e CPU. Antes de cada execução é conferido se há ao menos 8 GiB de memória disponível; caso contrário, ela termina sem iniciar o modelo. A resposta HTTP local, resultado do verificador, tempo e pico RSS são gravados por execução. Diferentemente do experimento CLI do OLMoE, Qwen exige o gateway local; tempos não são diretamente comparáveis sem considerar esse custo e o estado do cache. O serviço foi configurado para até cinco tentativas retomáveis de download; o cliente concluiu com sucesso. Após os testes, o serviço e os processos Qwen estavam encerrados.

Antes da inferência real, um servidor HTTP simulado local exercitou o coletor: seleção válida foi aceita; ausência de S-MAX e sinalização de limite de geração foram rejeitadas. Esse ensaio verifica o procedimento de coleta, não a qualidade ou o funcionamento do Qwen.

### Resultados medidos

Na máquina local, o download fixado terminou com 49 arquivos de pesos e 19.398.115.600 bytes no diretório, incluindo metadados e cache local. Ambos os testes usaram o prompt integral reproduzido na comparação acima; para Qwen, um gateway local em loopback retornou a resposta bruta e contagem de tokens. O log do motor confirmou contexto 2048 e cache de 32 por camada.

| Limite de saída | Tempo total por processo | Pico RSS reportado | Tokens de entrada / saída | Término | Verificador |
|---|---:|---:|---:|---|---|
| 256 | 106,73 s | 6.554.164 KiB | 340 / 26 | `stop` | Aceita |
| 512 | 103,44 s | 6.555.636 KiB | 340 / 26 | `stop` | Aceita |

As duas respostas brutas foram idênticas e são JSON puro:

```json
{
  "sentence_ids": ["S-001", "S-002", "S-MAX"]
}
```

O verificador aceitou estrutura, IDs, frase máxima e referências. As frases produzidas pelo catálogo reportam p95 de 120 ms no primeiro período (`EVD-001-01`), 900 ms no segundo (`EVD-001-02`) e severidade máxima `media`, também referida a `EVD-001-02`. A frase sobre 5xx `S-003` não foi selecionada; a política atual permite seleção parcial e a triagem básica conserva as três observações. Não há inferência causal.

Uma única execução por teto e uma fixture não demonstram confiabilidade ou utilidade geral. Como ambos terminaram após 26 tokens com `stop`, aumentar o teto não alterou a resposta observada; os tempos não são uma comparação estatística. O tempo inclui inicialização e encerramento do processo local; o pico RSS é reportado por `/usr/bin/time` e não constitui soma simultânea de todos os processos. A comparação com OLMoE é indicativa: Qwen usou gateway HTTP local, motor diferente e estado de cache possivelmente diferente. O swap global observado na máquina era aproximadamente zero antes da preparação e 1,5 GiB após os testes; não foi medido quanto dessa mudança se deve ao modelo. Os logs e JSON completos ficam localmente em `.local/story021-qwen-experiment/` e são ignorados pelo Git; os resultados essenciais estão reproduzidos acima.

A seleção do modelo e sua integração permanecem pendentes. A avaliação das outras duas fixtures foi executada posteriormente e consta abaixo. Permanecem pendentes avaliação adversarial com o modelo, confiabilidade, limites operacionais, protocolo e decisão do PO. Não transformar os dois resultados em aprovação de arquitetura ou evidência de fim a fim.


## Avaliação Qwen nas outras duas fixtures — 2026-11-01

Após o teste de INC-001, executaram-se quatro inferências locais reais com o mesmo Qwen, configuração, controles, timeout e verificador da comparação anterior. Os catálogos mudam conforme a fixture; cada limite foi executado uma vez por incidente. Os processos terminaram com código 0 e motivo `stop`. Tempo inclui inicialização e encerramento, e pico RSS não é soma simultânea dos processos.

| Incidente | Teto | Tempo | Pico RSS | Tokens de entrada / saída | Seleção | Resultado |
|---|---:|---:|---:|---:|---|---|
| INC-002 | 256 | 102,15 s | 6.553.728 KiB | 336 / 26 | S-001, S-002, S-MAX | Aceita |
| INC-002 | 512 | 102,40 s | 6.555.376 KiB | 336 / 26 | S-001, S-002, S-MAX | Aceita |
| INC-003 | 256 | 102,53 s | 6.552.724 KiB | 329 / 33 | S-001, S-002, S-003, S-MAX | Aceita |
| INC-003 | 512 | 101,33 s | 6.555.272 KiB | 329 / 33 | S-001, S-002, S-003, S-MAX | Aceita |

Em INC-002, S-MAX e S-002 citam EVD-002-02, sinal 5xx de 20%, e S-001 cita EVD-002-01. A observação de CPU S-003 não foi selecionada. Em INC-003, S-001, S-002 e S-003 citam EVD-003-01, EVD-003-02 e EVD-003-03, respectivamente; S-MAX cita EVD-003-02. As respostas de 256 e 512 foram idênticas dentro de cada fixture. No conjunto das três fixtures houve seis respostas aceitas em seis execuções controladas; não extrapolar essa proporção para confiabilidade em outros incidentes.

Os prompts seguintes foram enviados cada um em uma única mensagem, em ambas as execuções da fixture correspondente:

**INC-002**

```text
Selecione e ordene IDs das frases abaixo para explicar o incidente. Inclua obrigatoriamente S-MAX. Retorne somente um objeto JSON com a chave sentence_ids e uma lista de IDs, sem texto extra e sem IDs repetidos. S-MAX: Severidade máxima alta, determinada pelo sinal 2. S-001: Sinal 1: http_5xx_rate = 1.0 percent, de 2026-10-01T10:00:00+00:00 até 2026-10-01T10:05:00+00:00 (fim exclusivo); nível normal. S-002: Sinal 2: http_5xx_rate = 20.0 percent, de 2026-10-01T10:05:00+00:00 até 2026-10-01T10:10:00+00:00 (fim exclusivo); nível alta. S-003: Sinal 3: cpu_utilization = 92 percent, de 2026-10-01T10:05:00+00:00 até 2026-10-01T10:10:00+00:00 (fim exclusivo); nível normal.
```

**INC-003**

```text
Selecione e ordene IDs das frases abaixo para explicar o incidente. Inclua obrigatoriamente S-MAX. Retorne somente um objeto JSON com a chave sentence_ids e uma lista de IDs, sem texto extra e sem IDs repetidos. S-MAX: Severidade máxima alta, determinada pelo sinal 2. S-001: Sinal 1: memory_utilization = 60 percent, de 2026-10-01T10:00:00+00:00 até 2026-10-01T10:05:00+00:00 (fim exclusivo); nível normal. S-002: Sinal 2: memory_utilization = 97 percent, de 2026-10-01T10:05:00+00:00 até 2026-10-01T10:10:00+00:00 (fim exclusivo); nível alta. S-003: Sinal 3: cpu_utilization = 95 percent, de 2026-10-01T10:05:00+00:00 até 2026-10-01T10:10:00+00:00 (fim exclusivo); nível media.
```

Os casos de citação inexistente, afirmação livre sem apoio, duplicação e ausência de severidade foram novamente avaliados nos 18 testes controlados do verificador; insuficiência impede a criação de frases canônicas nesses testes. Isso não demonstra que um LLM foi efetivamente ignorado pela API, que ainda não possui triagem integrada, nem constitui ensaio adversarial do próprio modelo real. Logs e respostas completos ficam em `.local/story021-qwen-followup/`, fora do Git; os dados essenciais e prompts estão registrados aqui. Revisar esses limites e avaliar protocolo, timeout, concorrência e falhas antes de propor a integração.
