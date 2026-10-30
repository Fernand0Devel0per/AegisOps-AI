# Contratos de trabalho e continuidade

Comece por [AGENTS.md](../AGENTS.md). Esta pasta guarda estado versionável, não conversas completas nem código de aplicação.

| Pasta | Conteúdo |
|---|---|
| `specs/` | Solução técnica por história, interfaces necessárias, decisões e mapeamento dos critérios para validações |
| `activities/` | Atribuição delimitada: objetivo, entradas, saídas, restrições, passos e validação |
| `handoffs/` | Estado real ao interromper ou encerrar: arquivos, motivos, evidências, falhas e próximo passo |
| `templates/` | Modelos YAML para novos contratos |

O bootstrap está registrado em [SPEC-000](specs/SPEC-000.yaml), [ACT-000](activities/ACT-000.yaml) e [HANDOFF-000](handoffs/HANDOFF-000.yaml). A execução seguinte usa [SPEC-001](specs/SPEC-001.yaml) e [ACT-001](activities/ACT-001.yaml), ligadas à [STORY-001](../roadmap/stories/STORY-001.yaml). A atividade inicial ainda não foi executada.

## Regras de handoff

- Nenhuma atividade é `completed` sem validação executada e evidência registrada. Caso parcial/bloqueado deve usar o estado correspondente.
- Informar comando ou procedimento, resultado e caminho da evidência; não confundir revisão documental com testes da aplicação.
- Identificar testes não executados e motivo. Não esconder falha conhecida, dúvida ou trabalho pendente.
- Em `changed_files`, registrar caminho e motivo. Para muitos arquivos uniformes, listar cada caminho e apontar a justificativa comum; evitar copiar conteúdo de documentos ou código.
- Identificar o próximo papel/atividade, entradas necessárias e próximo passo concreto. Handoff para um papel não significa que uma mensagem foi enviada ou um agente foi iniciado.
- Versionar contratos, atualizações do roadmap e evidências com a entrega Git. Nunca afirmar commit/CI/publicação se não aconteceram.

Estados e convenções estão em [conventions.md](../doc/standards/conventions.md). O fluxo completo está em [workflow.md](../doc/standards/workflow.md).
