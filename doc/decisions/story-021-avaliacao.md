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
