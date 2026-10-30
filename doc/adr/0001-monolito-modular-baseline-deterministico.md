# ADR-0001 — Começar com monolito modular e baseline sem LLM

## Status

`accepted`. Autoridade: decisão explícita do autor no plano original, seções 2.3, 4.1, 6 (Etapa 0), 10 e 14. Este registro formaliza a decisão preexistente, sem nova aprovação presumida. Não substitui outro ADR.

## Data

2026-10-30 — formalização no bootstrap.

## Contexto

O projeto começa localmente, com incidentes sintéticos e objetivo de aprendizado verificável. Ainda não há aplicação ou dados que justifiquem distribuição, múltiplos agentes ou análise probabilística.

## Problema ou necessidade

Estabelecer a menor primeira vertical capaz de classificar um incidente e citar evidências reproduzíveis, sem antecipar dependências e custos da visão alvo.

## Alternativas consideradas

1. Monolito modular com regras determinísticas: opção inicial definida pelo plano.
2. Microsserviços e broker desde o início: maior operação e contratos distribuídos sem carga comprovada.
3. LLM e framework multiagente na primeira vertical: incerteza adicional e dificuldade de distinguir ganho do baseline.

## Decisão

Começar como monolito modular com pipeline simples. A primeira vertical recebe incidente sintético e retorna severidade e evidências sem LLM. Introduzir ferramentas, persistência, orquestração e análise LLM apenas nas etapas justificadas. Não fixa framework, banco, esquema completo ou árvore interna de módulos.

## Justificativa

Reprodução offline e regras explícitas permitem criar um baseline testável para comparações futuras. As alternativas adicionam custo e modos de falha antes de haver uma necessidade demonstrada.

## Consequências positivas

- Execução inicial sem provedor pago ou credenciais reais.
- Classificações reproduzíveis e testes de limiares, dados faltantes e evidência.
- Menor superfície operacional enquanto o domínio é descoberto.

Estes são benefícios esperados do design, não métricas já obtidas.

## Consequências negativas e trade-offs

- Não exercita distribuição nem a análise por LLM na primeira entrega.
- Regras precisam de definição e manutenção; não generalizam automaticamente.
- Fronteiras internas terão de ser revistas com aprendizado e requisitos posteriores.

## Riscos

Regras inadequadas podem gerar severidade enganosa; fixtures e aceite explícito devem vir antes da implementação. Evidência de carga, duração, retomada ou qualidade pode motivar novo ADR. Não converter o monolito em conjunto de abstrações vazias por antecipação.

## Referências

- [Plano original](../../AegisOps_AI_Plano_do_Zero.md), seções 2.3, 4.1, 6, 10 e 14.
- [Arquitetura](../architecture/overview.md).
- [STORY-004 — gate de descoberta](../../roadmap/stories/STORY-004.yaml).
