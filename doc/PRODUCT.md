# AegisOps AI — proposta de produto

## Estado

Proposta documental da [STORY-001](../roadmap/stories/STORY-001.yaml), aceita pelo Product Owner (PO) em 2026-10-30 para concluir a ACT-001. O PO aprovou severidade e verificação determinísticas, explicação por LLM local e resultado básico em caso de falha do LLM, conforme o [ADR-0002](adr/0002-llm-local-primeira-vertical.md). A aplicação e as capacidades descritas abaixo ainda não estão implementadas. O aceite da descoberta completa depende do gate da [STORY-004](../roadmap/stories/STORY-004.yaml).

## Problema

Na investigação de degradação de um serviço, sinais e documentação operacional podem estar dispersos.
Correlacioná-los exige trabalho humano e pode levar a conclusões sem evidência verificável.
O produto propõe apoiar a triagem com informações rastreáveis, preservando a decisão humana.

## Usuário e decisão

**Usuários indicados pelo PO:** desenvolvedores, profissionais de DevOps e outras pessoas responsáveis pela checagem de um incidente. No contexto inicial de demonstração local, eles precisam decidir o que priorizar e quais sinais examinar a seguir, considerando a severidade indicada, as evidências disponíveis e suas limitações. O PO concordou com essa decisão operacional. A classificação é apoio à decisão, não autorização para modificar infraestrutura.

A resposta do PO e a continuidade da revisão estão registradas em [Q-001](decisions/open-questions.md) e no [HANDOFF-001](../agents/handoffs/HANDOFF-001.yaml).

## Jornada

Fluxo proposto para uma investigação sintética, ainda não implementado:

1. A pessoa seleciona ou fornece um incidente sintético com os sinais disponíveis no cenário local.
2. A futura triagem determinística examina os sinais segundo critérios explícitos a definir e identifica eventual insuficiência de informação.
3. Regras verificam as referências às evidências; o LLM local explica o resultado sem determinar a severidade. A explicação e suas referências precisam passar pelas verificações definidas antes da apresentação.
4. O resultado previsto apresenta severidade, evidências verificadas, explicação disponível e limitações. Se o LLM falhar, apresenta o resultado básico e sinaliza a indisponibilidade.
5. A pessoa examina o resultado e decide a prioridade e as próximas verificações. Uma associação entre sinais não comprova causa; eventual hipótese deve ser identificada como tal.

## Primeira vertical

**Entrada prevista:** incidente sintético e seus sinais disponíveis. **Saída prevista:** classificação determinística de severidade, evidências rastreáveis e explicação por LLM local, sujeita à verificação, com indicação de informação insuficiente quando aplicável. Se a explicação falhar ou não passar na verificação, a saída básica de severidade e evidências continua disponível e sinaliza a limitação. O significado de severidade, os sinais necessários e o comportamento preciso para dados faltantes ainda serão definidos; não há limiares ou esquema completo aprovados nesta proposta.

A vertical será local, com Colibri para a explicação, sem remediação e sem acesso a sistemas de terceiros durante a investigação. O download inicial do modelo requer internet; a reprodução do resultado básico não exige credenciais nem serviço pago. A integração é planejada, não implementada; o papel do modelo e o fallback foram aprovados no [ADR-0002](adr/0002-llm-local-primeira-vertical.md).

## Capacidades previstas

Após a primeira vertical, o plano prevê evoluções graduais: recuperação de runbooks com fontes verificáveis e análise ampliada com hipóteses, recomendações para análise humana e avaliação adicional. A instrumentação da plataforma deverá ser distinguida dos sinais do incidente. Essas capacidades são planejadas, sujeitas às histórias, evidências e decisões pertinentes; nenhuma está entregue por esta atividade.

## Limites

- Usar dados sintéticos ou autorizados, inicialmente em ambiente local, sem credenciais ou serviços pagos necessários para o baseline.
- Consultas futuras devem respeitar escopo e limites, com documentos externos tratados como dados não confiáveis. A primeira vertical não acessa terceiros.
- Não executar alterações de infraestrutura ou remediação automática; decisões operacionais permanecem com pessoas.
- Não afirmar causa raiz automática, ganhos medidos ou confiança sem evidência. Distinguir observações de hipóteses e sinalizar lacunas.
- A visão mais ampla de runbooks e análise não é parte da primeira vertical; tecnologias e arquitetura adicionais dependem de justificativa e das decisões aplicáveis.

## Premissas e questões

- **Usuários e decisão:** o PO indicou desenvolvedores, profissionais de DevOps e outros responsáveis pela checagem, e concordou com a decisão de priorizar o incidente e escolher os sinais a examinar. Ver [Q-001](decisions/open-questions.md).
- **Em aberto:** sinais, unidades, períodos, regras de severidade e limiares ([Q-002](decisions/open-questions.md)); critérios observáveis e comportamento em falhas ou ausência de evidência ([Q-003](decisions/open-questions.md)). Os cenários e contratos serão tratados nas histórias próprias, sem antecipar sua aprovação.
- **LLM local:** o PO aprovou seu uso para explicação e o fallback; versão, modelo definitivo, avaliação e critérios precisos de verificação permanecem em aberto em [Q-016](decisions/open-questions.md). Uma inferência exploratória não comprova qualidade.
- **Gate humano pendente:** o PO avaliará produto, cenários e requisitos na [STORY-004](../roadmap/stories/STORY-004.yaml), conforme [Q-015](decisions/open-questions.md). A revisão desta proposta não constitui aceite da descoberta completa.

## Referências

- [Plano original local](../AegisOps_AI_Plano_do_Zero.md), seções 1, 2, 6 e 11: problema, princípios, etapas e primeira entrega.
- [ADR-0001](adr/0001-monolito-modular-baseline-deterministico.md): decisão histórica de monolito modular e triagem determinística.
- [ADR-0002](adr/0002-llm-local-primeira-vertical.md): alteração aprovada para explicação por LLM local na primeira vertical.
- [Questões abertas](decisions/open-questions.md): responsabilidades e momentos das decisões pendentes.
- [SPEC-001](../agents/specs/SPEC-001.yaml) e [ACT-001](../agents/activities/ACT-001.yaml): contrato e validação desta proposta.
