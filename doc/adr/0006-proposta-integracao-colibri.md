# ADR-0006 — Proposta para integração local da explicação

## Status

`proposed`; aguarda decisão do Product Owner. Complementa os ADRs 0002 e 0004 sem substituí-los. Nenhuma integração está aprovada ou implementada por este documento.

## Contexto e evidências

A STORY-021 exige explicação local avaliada antes da integração. O PO aprovou Colibri como direção, mas não o modelo, protocolo ou limites (Q-007/Q-016). Em [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml) consta um teste isolado de Colibri no commit `e0db083cdc9e563e0766cc6fc661ef23c32298e0` com OLMoE-1B-7B-0125-Instruct int8: 34,49 s, pico RSS de 3.516.808 KiB, resposta truncada e referência a logs ausentes. Uma chamada não avalia seleção de IDs nem comprova qualidade, licença, concorrência ou estabilidade. Modelo convertido e código existem localmente, fora do repositório; não estão garantidos para outro clone.

A documentação local desse commit apresenta `coli serve`, com interface HTTP compatível com `/v1/chat/completions`, e `coli run` como processo CLI. O servidor e esse protocolo ainda não foram exercitados pelo AegisOps. O plano original foi parcialmente substituído pelo ADR-0002: a primeira vertical requer LLM, com resultado básico disponível em falha.

## Alternativas

1. **Candidata para experimento:** Colibri nesse commit e OLMoE int8 já disponível, servidor manual em `127.0.0.1` e cliente HTTP de biblioteca padrão, sem SDK novo. Usar resposta não streaming e JSON restrito de IDs; verificar de forma independente. Configuração sem URL arbitrária ou proxies; nenhuma chamada a terceiros. Não pressupõe que o modelo esteja aprovado definitivamente. Mais memória e um processo local separado; servidor persistente reduz custo de carga, mas exige estudar concorrência, limites, interrupção e encerramento.
2. **CLI por chamada:** processo local isolado e tempo máximo controlável, porém carga repetida, parsing de saída de terminal e ciclo de vida mais complexos; o único teste prévio em modo CLI truncou. Sem medição comparativa para esta tarefa.
3. **Adiar modelo/adaptador e manter apenas avaliação do verificador com respostas simuladas:** reproduzível e independente de pesos, mas não satisfaz AC-01 nem demonstra explicação por LLM. Uma seleção simulada não é inferência.

## Proposta para decisão

Autorizar como **candidato experimental**, não modelo definitivo, a alternativa 1, sujeita à avaliação prévia das três fixtures e casos adversariais, verificação da licença e documentação de reprodução antes da integração. Propor um pedido por vez; limite inicial de 120 s por chamada, saída máxima de 128 tokens e resposta HTTP de até 64 KiB; nenhuma repetição automática; contexto e tamanho máximo de entrada precisam ser calibrados com os cenários e registrados antes da integração. Um timeout de cliente não garante cancelamento da inferência no servidor: demonstrar cancelamento/limite no processo ou manter essa limitação explícita antes de aprovar o uso. Memória deve ser limitada no processo local; orçamento anterior de modelo de 5 GB não é limite total de RSS. Não foi demonstrado que esses valores sejam suficientes ou seguros.

O PO pode escolher outra alternativa ou limites. Se o candidato não cumprir a avaliação, preservar a saída determinística e voltar ao PO com evidências, sem promover a opção a decisão aceita. Entrada inválida e insuficiente não fazem chamada; falha ou rejeição aciona fallback. Integração só após decisão explícita e avaliação satisfatória.

## Consequências e riscos

HTTP local acrescenta fronteira entre processos e demanda restringir loopback, redirecionamentos, proxy, volume, duração e concorrência. Dados sintéticos e texto externo não são instruções confiáveis. Referências resolvíveis não provam apoio semântico; avaliar o conteúdo das frases, além da estrutura. Os números propostos são limites experimentais, não medições de desempenho nem compromissos de produção. A escolha não autoriza serviço pago, envio de dados remotos, publicação nem tag.

## Referências

[Requisitos](../REQUIREMENTS.md), [ADR-0002](0002-llm-local-primeira-vertical.md), [ADR-0004](0004-api-local-contratos-http.md), [questões abertas](../decisions/open-questions.md), [STORY-021](../../roadmap/stories/STORY-021.yaml).
