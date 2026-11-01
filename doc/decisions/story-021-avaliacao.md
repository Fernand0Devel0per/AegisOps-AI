# Avaliação preliminar da explicação — STORY-021

Estado: fatia independente avaliada antes de integrar qualquer modelo ou endpoint. Não é avaliação da qualidade de um LLM e não conclui AC-04. A especificação está em rascunho e a proposta de integração aguarda decisão em [ADR-0006](../adr/0006-proposta-integracao-colibri.md).

## Política avaliada

A saída básica vem de `triage_incident`; um catálogo de frases é gerado de seus valores, métricas, períodos, níveis e evidências, sem texto livre de entrada. `S-MAX` refere-se ao primeiro sinal no nível máximo; cada observação tem frase própria. Uma seleção deve ser um objeto contendo exclusivamente `sentence_ids`: IDs existentes, únicos, com `S-MAX`. O verificador confere o catálogo calculado, os IDs e vínculos de evidência a sinal na entrada validada; a saída é a sequência de objetos canônicos selecionados, sem texto adicional. Esse módulo ainda não solicita LLM nem monta resposta HTTP.

## Casos e resultados controlados

A suíte [test_explanation.py](../../tests/unit/test_explanation.py) executada antes da integração confronta os máximos das três fixtures com valores e IDs esperados, e verifica ordem de uma seleção válida. Rejeita objeto malformado, IDs inexistentes ou duplicados, ausência da frase máxima, texto livre com afirmação sem apoio, catálogo adulterado com alegação causal, evidência inexistente ou ligada a outro sinal e evidência removida da fonte e divergência entre observação e sinal. Uma entrada válida sem sinais não gera catálogo de explicação. A suíte completa passou com 116 testes em 1,94 s; isso inclui 18 testes novos, não 116 casos independentes de avaliação de modelo.

Estes são testes sintéticos e sobretudo de conformidade e segurança do mecanismo; os três exemplos máximos e um período são comparados a expectativas explícitas, não há medição representativa de utilidade ou análise semântica exaustiva de cada frase. Referências resolúveis não provam que afirmações sejam verdadeiras no mundo real. Uma afirmação não apoiada não é representável como texto retornado pelo modelo sob esta política; o teste de adulteração avalia proteção do catálogo, não capacidade de o verificador julgar texto livre arbitrário.

## Antes da integração

Após decisão do PO, avaliar o candidato real e a configuração aprovada com as três fixtures, resposta estruturada completa, IDs inexistentes/duplicados, alegações livres, dados insuficientes e falhas; registrar entradas, versões, critério, resultados, tempo e limites sem inventar métricas. Validar licença e gerenciamento de tempo, memória e processo. Se o modelo não produzir seleção válida ou o isolamento não for adequado, não concluir a integração e voltar ao PO. O experimento de [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml) foi exploratório e não cumpre esta avaliação.
