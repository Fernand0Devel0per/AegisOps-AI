# Aceite humano — STORY-061, RICH-01 v1.0.0

Em 2026-11-08, o Product Owner informou nesta conversa que revisou os cinco PDFs e os 13 julgamentos e aprovou RICH-01 v1.0.0 para **avaliação exploratória**. Informou que conferiu os hashes e que as respostas são sustentadas pelos documentos. Esse aceite é posterior e distinto da autorrevisão do executor registrada em [REVIEW](../../datasets/rich-documents/REVIEW.md) e no [HANDOFF-061](../../agents/handoffs/HANDOFF-061.yaml).

O alcance informado inclui RD-01 a RD-05, as seis páginas, Q01–Q11 e suas unidades, períodos, relações e evidências, e as ausências Q12–Q13 exclusivamente no corpus indicado. Inclui os grupos atuais para exploração, sem partição independente ou teste cego, e os critérios de integridade, proveniência, reprodução e separação de dados.

## Identificação da revisão

O aceite se aplica ao conteúdo versionado no commit local `90f009f`, com os seguintes identificadores verificados novamente no encerramento:

- Manifesto: SHA-256 `f9a0f97730c9fe7366c0dbcfc3843113565a43b0217ee41367b44e4ef3dd787a`.
- Perguntas: SHA-256 `e21061f00d88453da2920c38232fd12c7a75e8eafe093f7b24618f43bae57fcd`.
- Gabaritos: SHA-256 `7860c4e2eb8b84fffa3c9383da5735ae88bf5659d97ef211e3daa6899f5771ee`.
- Os cinco hashes de PDF constam do [manifesto](../../datasets/rich-documents/manifest.yaml), cujo hash está acima; todos foram conferidos pelo validador e pelo PO.

Os campos `human_review: pending` e as menções à revisão humana pendente dentro do arquivo de gabaritos são o **registro histórico do momento de sua geração**, preservado byte a byte para não alterar o artefato aprovado. O estado efetivo posterior de Q01–Q13 é aprovado para o escopo acima, conforme este registro; consumidores devem verificar os hashes antes de aplicar esse aceite. Não editar o arquivo para simular que o aceite existia antes da revisão. O PO informou aceite abrangente desses julgamentos, sem registrar anotações individuais adicionais.

## Ressalvas do PO

1. Amostra pequena, sintética e exploratória; o aceite não demonstra qualidade de ingestão ou recuperação.
2. Antes de qualquer divisão de desenvolvimento e avaliação, revisar relações entre grupos, especialmente Q12/Atlas e Q13/Lume, e evitar vazamento. A ausência refere-se ao corpus inteiro; a exposição dos documentos e consultas impede declarar teste independente ou cego.
3. Q12–Q13 são ausências somente neste corpus e versão; conteúdo não julgado não vira negativo.
4. Alteração de documentos, hashes ou gabaritos exige versionamento e avaliação do impacto na revisão e no aceite.
5. Nenhum extrator, estratégia de chunking, mecanismo de recuperação ou RAG foi aprovado por este aceite.

## Conferência de critérios e Definition of Done

| Critério | Evidência e conclusão |
|---|---|
| AC-01 | Cinco famílias e seis páginas; inspeção visual do executor em [REVIEW](../../datasets/rich-documents/REVIEW.md), seguida da revisão declarada pelo PO. Limites de páginas e tamanho verificados. |
| AC-02 | [Manifesto](../../datasets/rich-documents/manifest.yaml), [gabaritos](../../datasets/rich-documents/judgments.yaml), hashes e verificador estrutural; o PO confirmou suporte das respostas e ausências na versão indicada. |
| AC-03 | Separação, grupos e limitações em [REVIEW](../../datasets/rich-documents/REVIEW.md); aceite exploratório do PO sujeito à revisão adicional de grupos antes de partição. |
| DoD | Critérios e revisão humana documentados, validações e limites no [HANDOFF-061](../../agents/handoffs/HANDOFF-061.yaml); história, atividade e índice atualizados conjuntamente. |

O validador verifica correspondências estruturais, não substitui julgamento semântico. A revisão do PO foi informada pelo próprio PO; o executor não observa nem reproduz independentemente o processo humano de revisão.
