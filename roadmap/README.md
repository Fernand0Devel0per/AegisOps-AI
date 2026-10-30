# Planejamento oficial

[index.yaml](index.yaml) cataloga épicos, histórias, prioridades, dependências e estados. Os arquivos em `epics/` e `stories/` contêm o contrato de cada entrega. O [plano original](../AegisOps_AI_Plano_do_Zero.md) é a origem dos requisitos; o índice representa o estado atual, sem reescrever a fonte.

## Ordem inicial

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

`ready` exige escopo delimitado, dependências concluídas, critérios verificáveis, spec suficiente e atividade preparada. `done` exige evidência por critério, validação registrada, revisão e handoff. Revisão do PO é obrigatória no gate de descoberta e em decisões/requisitos que a exijam. Consulte [workflow](../doc/standards/workflow.md).

Épico `ready` significa que existe ao menos uma história pronta; não significa fase concluída. Épico `done` exige suas histórias concluídas e critérios de saída demonstrados. As dependências iniciais entre fases seguem ordem educacional conservadora; podem ser refinadas sem tornar uma tecnologia opcional pré-requisito técnico obrigatório.

## Releases e issues

`v0.1.0` é uma candidata futura: API recebe incidente sintético e retorna triagem/evidências consistentes, com testes reproduzíveis. Depende das Etapas 0–2; não requer LLM. Não há tag nem release criada. O índice contém um marco explícito, sem indicar funcionalidade pronta.

IDs locais não são números de issues do GitHub. Não foram abertas issues remotas. Quando houver autorização para publicação, vincular IDs e issues/PRs sem duplicar o catálogo de estados em outra base manual.

Use [story.template.yaml](templates/story.template.yaml) e as [convenções](../doc/standards/conventions.md). Valide com `python3 scripts/validate_repository.py` na raiz.
