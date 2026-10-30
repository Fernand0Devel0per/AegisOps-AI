# Workflow agent-first

```text
Plano original → Épico → História → Especificação técnica → Atividade atribuída
  → Implementação pelo agente → Testes e validação → Revisão → Handoff
  → Atualização da história → Próxima atividade
```

Implementação pode produzir documentos na descoberta ou código nas etapas autorizadas. O bootstrap atual termina antes da implementação da aplicação.

| Etapa | Entrada mínima | Saída mínima / condição para avançar |
|---|---|---|
| Plano | Fonte original e instrução atual | Propósito, restrições e diferenças compreendidos; fonte preservada |
| Épico | Etapa e objetivos do plano | Escopo, dependências, entregas e critérios de saída; sem adoção automática de stack |
| História | Recorte de um épico | Objetivo, escopo, critérios observáveis, validação, dependências e prioridade |
| Especificação | História refinada e contexto | Contratos necessários, desenho proporcional, mapeamento de todos os ACs, riscos e ADRs relevantes; perguntas bloqueadoras resolvidas |
| Atividade | Spec suficiente e dependências concluídas | Papel, responsabilidade, entradas existentes, saídas delimitadas, restrições e procedimentos de validação; história pode ficar `ready` |
| Implementação | Atividade preparada e escopo autorizado | Artefatos que atendem ao contrato; testes pertinentes e documentação afetada atualizados |
| Testes e validação | Entrega concreta | Comandos/procedimentos, resultados, evidências e testes não executados com motivo; falhas não escondidas |
| Revisão | Diff e validação verificáveis | Observações resolvidas ou pendências explícitas; aceite do PO quando necessário; decisão registrada no handoff |
| Handoff | Estado e revisão da atividade | Arquivos e motivos, decisões, validações, limitações, trabalho pendente e destino; sem duplicar código |
| Atualização da história | Handoff e evidência por AC | História/índice coerentes; `done` somente com todos os ACs e DoD satisfeitos |
| Próxima atividade | Estado atualizado e handoff legível | Próximo contrato e dependências identificados; agente novo consegue continuar sem conversa |

## Critérios de pronto

Para entrar em `ready`, a história deve ter escopo pequeno, dependências `done`, aceite verificável, spec `ready` e atividade `pending` preparada. Histórias futuras marcadas para refinamento não entram diretamente em execução. Perguntas futuras não bloqueiam trabalho independente; pergunta que altera o aceite da atividade precisa de resolução antes do trabalho dependente.

Para concluir uma atividade, registrar pelo menos uma validação executada, seu resultado e evidência recuperável. Não declarar concluída com validação falha relevante ao escopo. Registrar separadamente testes de aplicação ausentes por não haver implementação. Uma revisão automatizada ou autorrevisão deve ser identificada como tal, sem atribuir revisão humana inexistente.

Para história `done`, todos os ACs e DoD devem ter evidência, revisão deve estar registrada, e handoffs devem representar o trabalho realizado. Na Etapa 0, STORY-004 exige validação humana da descoberta, mesmo que histórias documentais anteriores tenham revisão de consistência pelo próprio agente.

Um handoff de bloqueio registra motivo, responsável/condição de desbloqueio e o que já foi validado. Não mudar a história para `done` enquanto faltarem critérios. Próximo agente lê arquivos, histórico Git quando existir e o handoff, não presume sucesso pelo resumo.

## Aplicação imediata

O bootstrap tem contrato retrospectivo em `SPEC-000/ACT-000` porque registra a execução explicitamente solicitada nesta sessão. O próximo contrato `SPEC-001/ACT-001` foi preparado antes de sua execução. `STORY-001` é a próxima história pronta; não produzir agora `doc/PRODUCT.md`, fixtures ou aplicação como se a descoberta estivesse aceita.

As etapas futuras devem respeitar a ordem educacional até revisão explícita. Orquestração e outros recursos opcionais podem terminar com recomendação de manter a solução simples, desde que a avaliação e a decisão tenham evidência. Não forçar uma tecnologia para satisfazer um número de etapa.
