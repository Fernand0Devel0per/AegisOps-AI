# ADR-0002 — Explicação por LLM local na primeira vertical

## Status

`accepted` em 2026-10-30 pelo Product Owner (PO), que solicitou Colibri e LLM local desde a primeira vertical e concordou que regras determinem a severidade e verifiquem as evidências, que o LLM explique o resultado e que a saída básica permaneça disponível se ele falhar. A aprovação está registrada no [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml).

Este ADR substitui parcialmente o [ADR-0001](0001-monolito-modular-baseline-deterministico.md): a exclusão de LLM na primeira vertical deixa de valer. O monolito modular e o núcleo determinístico de severidade e evidências permanecem. A aceitação não escolhe um modelo definitivo nem comprova sua qualidade.

## Contexto e problema

O PO deseja uma explicação local para a triagem, sem custo de serviço pago nem comprometimento da memória da máquina. O plano original previa introduzir LLM mais tarde; a mudança foi solicitada durante a revisão da STORY-001. Não há aplicação ou integração implementada.

## Alternativas consideradas

1. **Escolhida:** regras determinam a severidade e verificam referências de evidência; um LLM local explica o resultado. Em falha ou indisponibilidade do LLM, a saída básica permanece disponível com a limitação sinalizada.
2. Usar o LLM também para determinar severidade: adiciona variabilidade à classificação e exigiria avaliação adicional; não foi a opção escolhida pelo PO.
3. Introduzir LLM somente depois: reduz dependências iniciais, mas não atende à direção escolhida pelo PO.

## Decisão

Na primeira vertical, um incidente sintético produz severidade e evidências por regras determinísticas. O Colibri é a ferramenta local solicitada para executar um LLM que explique o resultado; o modelo não determina a severidade nem é autoridade para validar evidências. Regras externas ao LLM devem verificar referências; explicação inválida não deve ser apresentada como confiável. Em falha, indisponibilidade ou rejeição da explicação, a saída básica continua disponível e a limitação é sinalizada. Detalhes dos contratos, mensagens, limites e casos de falha serão definidos nas histórias aplicáveis.

A primeira vertical mantém execução local, dados sintéticos, sem serviço pago obrigatório, sem remediação e sem consulta a sistemas de terceiros durante a investigação. O download inicial do modelo requer internet. Referência existente é necessária, mas não prova que uma afirmação seja sustentada: avaliação e política de evidência precisam tratar essa limitação.

## Viabilidade inicial

A máquina consultada possui cerca de 15 GiB de RAM; a GPU integrada compartilha memória. O [Colibri](https://github.com/JustVugg/colibri) lista o OLMoE de 7B como opção que exige preparação manual. Uma inferência exploratória em CPU, limitada a 64 tokens, terminou em 34,49 segundos com pico RSS de 3516808 KiB; a resposta foi truncada e mencionou logs não fornecidos. O processo tinha orçamento de modelo de 5 GB e serviço limitado a 7 GiB. Evidências e limites do experimento estão no [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml). Isso não garante qualidade, estabilidade ou velocidade em outras cargas.

## Consequências e pendências

- A primeira entrega inclui explicação local e fallback, além do núcleo determinístico; aumenta o trabalho de avaliação, integração e tratamento de falhas.
- OLMoE é candidato testado, não modelo definitivo aceito. Versões, licença, qualidade em português, memória e latência exigem avaliação antes da adoção.
- Definir cenários, regras, evidências, saídas e critérios de falha observáveis antes da implementação. A avaliação deve incluir citações inexistentes, afirmações sem apoio e dados insuficientes.
- Refinar histórias futuras e o marco para cumprir esta decisão sem antecipar implementação; o aceite completo da descoberta permanece na STORY-004.

## Referências

- [Produto](../PRODUCT.md), [questões abertas](../decisions/open-questions.md) e [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml).
- [ADR-0001](0001-monolito-modular-baseline-deterministico.md) e [plano original](../../AegisOps_AI_Plano_do_Zero.md).
