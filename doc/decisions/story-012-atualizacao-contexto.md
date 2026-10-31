# Continuidade — atualização de contexto da STORY-012

Em 2026-10-31, o PO solicitou atualizar a [STORY-012](../../roadmap/stories/STORY-012.yaml) antes de seu refinamento, para refletir a conclusão da STORY-011 e as decisões aceitas para a primeira API.

A história agora aponta para os ADRs 0003 e 0004 e para o [HANDOFF-011](../../agents/handoffs/HANDOFF-011.yaml). Seu contexto registra os contratos independentes de transporte, a direção FastAPI e a necessidade de verificar versões e compatibilidade. Notas de refinamento identificam a entrada inválida de AC-02, a representação de IDs, a disponibilidade do catálogo, a saúde e a evidência de CI de AC-03. A alteração não cria critérios, altera o escopo ou antecipa desenho ainda não aprovado.

A branch existente `feat/story-012` foi atualizada com `origin/main` após o PR #2 da STORY-011, preservando o commit anterior da branch. A STORY-012 continua `backlog` com `refinement_required: true`; o índice permanece coerente e seus ponteiros permanecem na STORY-011 até existirem os contratos seguintes. Nenhuma SPEC ou ACT da STORY-012 foi criada nesta atualização.

## Validação e revisão

- `python3 scripts/validate_repository.py`: passou após a alteração.
- `python3 scripts/validate_incidents.py`: passou para as três fixtures existentes.
- `git diff --check` e `git diff --cached --check`: passaram após a alteração.
- Autorrevisão documental pelo executor: comparou a história com o ADR-0004 e preservou os três critérios e o estado do índice; não representa revisão humana da alteração.
- Testes da aplicação e CI remota desta mudança documental não foram executados. O validador documental não foi alterado, portanto seu self-test não foi necessário.

## Próximo passo

Quando o PO autorizar a execução, refinar a STORY-012, produzir a SPEC e a ACT a partir dos templates e mapear seus critérios. Registrar os testes de compatibilidade das dependências HTTP antes da adoção, conforme ADR-0004. O prompt local em `.local/handoffs/CONTINUIDADE-STORY-012.md` complementa este registro; a continuidade essencial permanece nos arquivos versionados.
