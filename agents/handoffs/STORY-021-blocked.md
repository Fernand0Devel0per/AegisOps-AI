# Bloqueio anterior à atividade da STORY-021

Data: 2026-10-31. Destinatário: Product Owner e próximo agente.

A STORY-021 permanece em `backlog`, bloqueada antes do refinamento e da
implementação. O pedido exige STORY-020 `done`, STORY-012 concluída e gate do
EPIC-001 concluído na base escolhida. Nenhuma SPEC ou ACT foi criada para esta
história; este registro não representa uma atividade iniciada.

## Base e evidências

- `git fetch --prune origin` passou. `origin/main` permaneceu em
  `3b9d48d732408b237937569b478302fd5e84d6ea`; a lista de branches remotas não
  inclui uma branch da STORY-020. Os arquivos e o índice de `origin/main`
  registram [STORY-020](../../roadmap/stories/STORY-020.yaml) `backlog`,
  [STORY-012](../../roadmap/stories/STORY-012.yaml) `in_review` e
  [EPIC-001](../../roadmap/epics/EPIC-001.yaml) `in_progress`.
- A branch `feat/story-021` parte de `67263ace4509eeab7ecebbc225eef12e912f8202`,
  que tem `origin/main` como ancestral e acrescenta apenas o registro anterior
  de bloqueio da STORY-020. O workspace estava limpo antes da troca; o histórico
  e a branch anteriores foram preservados. Os mesmos estados valem nessa base.
- [HANDOFF-012](HANDOFF-012.yaml) registra revisão e verificação do head mais
  recente pendentes; o [bloqueio da STORY-020](STORY-020-blocked.md) registra
  a necessidade de decisão do PO sobre a STORY-012 e o gate. O merge de PR não
  comprova por si só esses fechamentos. Não foi presumido aceite humano.
- O plano original está disponível localmente; sua leitura para a atividade e as
  demais leituras técnicas ficam pendentes até que as dependências sejam cumpridas.

## Continuidade

O PO deve revisar a entrega da STORY-012 e decidir sobre seu fechamento e o gate
do EPIC-001, registrando decisão e evidências na base, e orientar a conclusão da
STORY-020. Após STORY-020 `done` e demais condições comprovadas na base atualizada,
retomar a STORY-021, conferir IDs disponíveis, ler as fontes técnicas e preparar
SPEC e ACT antes de qualquer implementação. As questões estão em
[Q-017 e Q-018](../../doc/decisions/open-questions.md).

## Validação e revisão

`python3 scripts/validate_repository.py` passou: 62 YAML, 11 épicos, 22
histórias e 27 Markdown; o validador não verifica o plano local. `git diff
--check` e `git diff --cached --check` passaram. Autorrevisão pelo executor:
estados, base, links e limites do registro conferidos; revisão independente
do impedimento permanece pendente.

Não foram executados instalação, testes de aplicação, Ruff, mypy, Pyright ou
validador de incidentes: não houve alteração de código, dependências ou fixtures.
Não houve avaliação de LLM, demonstração local, CI, revisão independente ou
aprovação humana. Não houve push, PR, publicação ou merge.
