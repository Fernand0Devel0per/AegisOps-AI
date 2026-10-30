# Escopo e adaptações do bootstrap

Data: 2026-10-30. Origem: pedido atual de bootstrap e [plano original](../../AegisOps_AI_Plano_do_Zero.md), seções 0, 6, 9, 13 e 14.

1. **Colaboração:** o plano propõe mentoria e código escrito pelo autor. O pedido atual autoriza preparação documental integral e um fluxo de desenvolvimento executado por agentes, com humano como PO. Esta instrução atual rege o bootstrap e o contrato operacional. Não é autorização para gerar a aplicação agora; o objetivo de estudo, explicação de trade-offs e validação humana permanece. Mudança futura de modo deve ser registrada.
2. **Diretório canônico:** usar `doc/`, conforme a estrutura solicitada agora. Os entregáveis `docs/PRODUCT.md`, `docs/REQUIREMENTS.md` e `docs/adr/` do plano passam a `doc/PRODUCT.md`, `doc/REQUIREMENTS.md` e `doc/adr/`. Não manter árvores duplicadas ou links para arquivos ainda inexistentes.
3. **Raiz:** usar a pasta existente `ia-work` como raiz; não mover o plano nem criar um repositório aninhado `AegisOps-AI/`. Havia somente o plano, sem Git, código ou instruções de agentes preexistentes. Git é inicializado localmente e os artefatos recebem um commit inicial, sem remoto ou publicação nesta execução.
4. **Plano preservado:** o pedido exige preservação do arquivo original, portanto a orientação da seção 14 de atualizá-lo a cada sessão é atendida por handoffs versionáveis e estados no roadmap. Não modificar o registro inicial original para simular progresso.
5. **Rastreabilidade:** `STORY-000`, `SPEC-000`, `ACT-000` e `HANDOFF-000` registram esta preparação já executada dentro da descoberta. `STORY-001` é a primeira atividade futura; não confundir bootstrap concluído com Etapa 0 concluída.
6. **Escopo da ferramenta auxiliar:** `scripts/validate_repository.py` valida documentos e contratos, não funcionalidades de negócio. `src/` permanece vazio com `.gitkeep`. Não foram criados esqueletos Python, dependências de runtime, serviços, datasets ficticiamente aprovados ou testes de aplicação.
7. **Histórico:** documentos recebem versionamento em um commit local do bootstrap. Licença, remoto e publicação continuam pendentes. O commit pode ser consultado por `git log -1`; sua criação não indica aceite humano de produto.

Estas são adaptações operacionais autorizadas pelo pedido, não novas decisões de arquitetura da aplicação. Por isso não geram ADR adicional. O ADR arquitetural aceito registra somente o ponto de partida já explícito no plano.
