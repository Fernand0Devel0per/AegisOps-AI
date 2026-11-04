# Planejamento oficial

[index.yaml](index.yaml) cataloga épicos, histórias, prioridades, dependências e estados. Os arquivos em `epics/` e `stories/` contêm o contrato de cada entrega. O [plano original](../AegisOps_AI_Plano_do_Zero.md) é a origem dos requisitos; o índice representa o estado atual, sem reescrever a fonte.

## Ordem inicial (histórico do bootstrap)

A sequência abaixo registra a preparação inicial; os estados atuais e a próxima atividade estão no índice. A Etapa 2 foi concluída e a Etapa 3 começou pelo estudo da SPIKE-030, agora em revisão.

1. `STORY-000`: bootstrap documental concluído; não é a conclusão da descoberta.
2. [STORY-001](stories/STORY-001.yaml): produto, usuário, decisão e limites. Está `ready`, com [SPEC-001](../agents/specs/SPEC-001.yaml) e [ACT-001](../agents/activities/ACT-001.yaml) pendente.
3. [STORY-002](stories/STORY-002.yaml): três incidentes sintéticos reproduzíveis e resultados esperados, após STORY-001.
4. [STORY-003](stories/STORY-003.yaml): entradas/saídas, regras de severidade, cinco critérios e ao menos três falhas, após STORY-002.
5. [STORY-004](stories/STORY-004.yaml): revisar evidências e obter validação do PO para encerrar a Etapa 0. O ADR-0001 já existe e deve ser respeitado.
6. [STORY-010](stories/STORY-010.yaml): primeiro trabalho de implementação Python, **somente depois** do gate de descoberta e da especificação/decisões de setup. Não está pronta para executar agora.

Há um épico por Etapa 0–10. A descoberta foi detalhada; histórias posteriores são recortes iniciais com `refinement_required: true`. Antes de movê-las para `ready`, reavaliar tamanho, dependências, critérios, decisões e especificação. Dividir novamente se uma história não couber em um incremento verificável. Não usar a existência de uma história como autorização para pular gates.

## Estados e manutenção

Estados de histórias e épicos: `backlog`, `ready`, `in_progress`, `blocked`, `in_review`, `done`. Prioridades: `high`, `medium`, `low`. Dependências são IDs de histórias no catálogo de histórias; épicos dependem de outros épicos. Não misturar os dois espaços.

O estado da história no arquivo e no índice deve coincidir. O mesmo vale para título, prioridade, épico e dependências catalogadas. IDs são estáveis; não renumerar ao reordenar prioridades. O catálogo duplica apenas esses metadados mínimos para permitir descoberta; descrição e critérios vivem no arquivo da história.

Estudos usam IDs `SPIKE-NNN` e o mesmo template, pasta `stories/`, catálogo e estados das histórias. Podem ser dependências diretas de histórias. No EPIC-003, a [SPIKE-030](stories/SPIKE-030.yaml) estuda fontes e avaliação própria antes de STORY-030 e STORY-031; tem proposta documentada e está em revisão, com SPEC-029 e ACT-029. A seleção documental e os rótulos exigem a revisão prevista no aceite; veja o [handoff](../agents/handoffs/HANDOFF-029.yaml).

`ready` exige escopo delimitado, dependências concluídas, critérios verificáveis, spec suficiente e atividade preparada. `done` exige evidência por critério, validação registrada, revisão e handoff. Revisão do PO é obrigatória no gate de descoberta e em decisões/requisitos que a exijam. Consulte [workflow](../doc/standards/workflow.md).

Épico `ready` significa que existe ao menos uma história pronta; não significa fase concluída. Épico `done` exige suas histórias concluídas e critérios de saída demonstrados. As dependências iniciais entre fases seguem ordem educacional conservadora; podem ser refinadas sem tornar uma tecnologia opcional pré-requisito técnico obrigatório.

## Releases e issues

`v0.1.0` permanece uma candidata sem tag ou release: a primeira vertical das Etapas 0–2 recebe incidente sintético e retorna triagem e evidências determinísticas, com explicação por LLM local verificada e fallback conforme ADR-0002. Sua implementação foi concluída, sem publicação da candidata. O estudo da Etapa 3 não é pré-requisito desse marco.

IDs locais não são números de issues do GitHub. Não foram abertas issues remotas. Quando houver autorização para publicação, vincular IDs e issues/PRs sem duplicar o catálogo de estados em outra base manual.

Use [story.template.yaml](templates/story.template.yaml) e as [convenções](../doc/standards/conventions.md). Valide com `python3 scripts/validate_repository.py` na raiz.
