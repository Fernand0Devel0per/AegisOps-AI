# Architecture Decision Records

ADRs registram decisões arquiteturais duráveis, alternativas e consequências. Use [0000-template.md](0000-template.md), reservando o próximo número livre. O [ADR-0001](0001-monolito-modular-baseline-deterministico.md) é aceito porque formaliza uma decisão inequívoca do plano, não porque uma nova escolha tenha sido aprovada nesta execução.

O [ADR-0002](0002-llm-local-primeira-vertical.md) registra a alteração aprovada pelo PO para a primeira vertical e substitui parcialmente o ADR-0001.

O [ADR-0003](0003-ambiente-python-qualidade.md) registra ambiente e ferramentas da STORY-010, aprovados pelo PO após teste isolado com Python 3.14.

O [ADR-0004](0004-api-local-contratos-http.md) registra as escolhas do PO para a primeira API; versões e compatibilidade da stack ainda serão verificadas antes da adoção.

Estados: `proposed` → `accepted`; uma decisão aceita pode tornar-se `superseded` por novo ADR ou `deprecated` por abandono documentado. Registre autor/autoridade da aceitação e relações com decisões anteriores. Não reescreva silenciosamente ADR aceito. Correções editoriais não podem mudar seu sentido.

Banco, comunicação entre serviços, autenticação, frameworks, padrões de integração, dependências estruturais e mudanças relevantes de arquitetura exigem ADR. Detalhes triviais de implementação não exigem registro. Candidatas da tabela de stack não são decisões aceitas.
