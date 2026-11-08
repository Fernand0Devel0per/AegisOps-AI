# ADR-0007 — Manter a vertical atual após comparação de workflow

## Status

`accepted` para a decisão de **não alterar** a arquitetura existente nesta comparação. Autoridade: o PO autorizou a STORY-050, incluindo a alternativa de manter o pipeline; a decisão técnica se limita a preservar o desenho já aceito no ADR-0001 e não representa aprovação do PO para uma nova arquitetura. Não substitui os ADRs 0001, 0002 ou 0006. O protótipo não é adotado.

## Data e contexto

2026-11-07. A STORY-050 compara a rota existente com um protótipo local de estado explícito, usando mocks e dados sintéticos. A exceção autorizada de dependência preserva a STORY-041 parcial e está documentada em [transição](../decisions/story-050-excecao-dependencia.md).

## Alternativas

1. Manter a rota e o pipeline atuais, já aceitos, sem dependências novas.
2. Integrar o protótipo de máquina de estados: dá visibilidade local aos passos, mas duplica coordenação, não provê retomada durável e não demonstrou melhora de qualidade.
3. Adotar framework ou persistência: não foram implementados nem medidos; introduzem dependência e custos que exigem proposta e aprovação específicas.

## Decisão e justificativa

Manter a solução atual para a vertical existente. O teste controlado observou equivalência de saída nos cenários comparados, com o mesmo núcleo e mocks, e o protótipo apenas acrescentou estado em memória e coordenação duplicada. Não há evidência de benefício suficiente para integrá-lo. Esta decisão não altera a API, Colibri, limites ou fallback, e não proíbe avaliação futura de workflow.

## Consequências e riscos

A solução atual mantém simplicidade e comportamento existente, mas não oferece histórico explícito de transições nem retomada por etapa. O protótipo ilustra inspeção em memória, não persistência, replay, qualidade de LLM ou operação real. Quando houver necessidade concreta desses recursos, preparar proposta, evidências e novo ADR e obter aprovação humana antes de mudança estrutural. As pendências da STORY-041 e as condições de autorização de inferência real permanecem intactas.

## Evidências

[Relatório de comparação](../architecture/workflow-evaluation.md), [testes](../../tests/evaluation/test_workflow_050.py), [STORY-050](../../roadmap/stories/STORY-050.yaml) e [ADR-0001](0001-monolito-modular-baseline-deterministico.md).
