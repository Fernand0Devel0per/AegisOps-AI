# ADR-0004 — Primeira API local e contratos HTTP

## Status

`accepted` em 2026-10-31 pelo Product Owner (PO), que examinou e aceitou as recomendações para a primeira API e solicitou seu registro ao encerrar a STORY-011. A evidência da decisão está no [HANDOFF-011](../../agents/handoffs/HANDOFF-011.yaml). Não substitui outro ADR: complementa o monolito modular e o núcleo determinístico dos [ADR-0001](0001-monolito-modular-baseline-deterministico.md) e [ADR-0002](0002-llm-local-primeira-vertical.md), e preserva o ambiente do [ADR-0003](0003-ambiente-python-qualidade.md).

A decisão escolhe a direção arquitetural da API futura. A API, o framework e as respostas HTTP ainda não estão implementados. A seleção de versões, teste de compatibilidade e instalação da stack permanecem para a atividade autorizada da STORY-012.

## Data

2026-10-31.

## Contexto

A STORY-011 implementou modelos e validação determinística independentes de transporte. A [STORY-012](../../roadmap/stories/STORY-012.yaml), ainda em backlog e sujeita a refinamento, prevê consulta local dos incidentes sintéticos e saúde, com erros estruturados. Triagem, integração de LLM, persistência e jobs não fazem parte dessa história. O sistema deve continuar reproduzível sem credenciais ou serviços pagos após preparação do ambiente.

## Problema ou necessidade

Definir uma primeira interface HTTP compreensível, com erros consistentes e uma tecnologia adequada ao objetivo de estudo e portfólio, preservando as regras do domínio e evitando infraestrutura antecipada.

## Alternativas consideradas

- **Rotas sem prefixo de versão:** nomes menores, mas a migração de contratos incompatíveis teria de ser definida posteriormente. Versão em cabeçalho mantém URLs estáveis, porém torna a consulta manual e o diagnóstico menos diretos. O prefixo `/v1` torna a versão visível e não exige criar outra versão agora.
- **Erros em JSON próprio ou no formato padrão do framework:** exigem menos configuração inicial, mas criam convenção própria ou acoplam consumidores aos detalhes da ferramenta. Problem Details padroniza os campos básicos e permite extensões.
- **Resposta na requisição ou jobs com `202`:** o segundo modelo pode acomodar trabalho demorado, mas adiciona estado, acompanhamento e recuperação de falhas. Consultas locais da primeira API serão respondidas na própria requisição.
- **FastAPI, Starlette ou Flask:** FastAPI oferece contratos tipados e documentação OpenAPI, ao custo de dependências como Pydantic e Starlette. Starlette deixa mais decisões de validação e documentação a cargo do projeto. Flask fornece uma base WSGI simples, com escolhas adicionais para contratos e documentação. As alternativas foram comparadas conceitualmente; nenhuma foi testada nesta atividade.

## Decisão

1. Usar FastAPI como framework da futura API, com camada HTTP responsável por receber requisições e traduzir respostas e erros. As regras existentes de incidente, sinal e evidência continuam no núcleo independente do framework; não duplicar regras de domínio em validadores de transporte.
2. Expor consulta individual por `GET /v1/incidents/{id}` e saúde por `GET /health`. O identificador mantém as regras de texto não vazio e unicidade já aceitas; não impor formato `INC-NNN` como requisito de domínio. O tratamento exato de caracteres de ID no transporte será detalhado na especificação da API.
3. `/health` indicará que a aplicação concluiu a inicialização e está apta a atender consultas locais. Validar o catálogo necessário na inicialização; se esta falhar, a aplicação não deve iniciar aceitando requisições. Divisão em liveness/readiness poderá ser avaliada quando houver necessidade operacional. LLM opcional não é requisito de saúde da consulta local.
4. Usar [Problem Details, RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html), com `application/problem+json`; incluir códigos de aplicação estáveis e, quando pertinente, detalhes de campos, sem expor valores sensíveis ou rastros internos. Requisição ou parâmetro inválido pode retornar `400`, incidente inexistente `404`, erro interno `500` e indisponibilidade temporária `503`. Um futuro corpo de requisição sintaticamente válido que viole o contrato de domínio pode retornar `422`; isso não cria endpoint de entrada nesta história. Uma fixture inválida é falha da aplicação, não erro atribuído ao cliente.
5. Responder na mesma requisição, sem jobs. A escolha entre `def` e `async def` dependerá do I/O efetivo, mantendo a interface síncrona para o consumidor. Em FastAPI, rotas `def` usam pool de threads; operações bloqueantes não devem bloquear diretamente um event loop. Não se presume ganho de desempenho sem medição.
6. A documentação OpenAPI é benefício esperado. Se a interface interativa for oferecida como parte da experiência offline, seus ativos devem ser locais; não pressupor que o padrão baseado em CDN funcione sem rede.

A decisão não fixa a criação de endpoint de escrita ou triagem, schema completo da investigação, CLI ou uma implementação de probes. O nome, versão e configuração do servidor ASGI, as versões exatas de FastAPI e dependências, eventuais detalhes de JSON e política de limites continuam para o refinamento da STORY-012 e etapas aplicáveis. Não restringir silenciosamente os IDs já aceitos nem implementar acesso por caminho de arquivo derivado de entrada sem controle explícito.

## Justificativa

O prefixo de versão ajuda a comunicar compatibilidade; Problem Details dá estrutura comum a falhas HTTP; e FastAPI favorece documentação de contratos e tipagem. São benefícios esperados, não medições do projeto. A preservação do núcleo evita fazer da validação HTTP uma segunda autoridade sobre os requisitos aceitos.

## Consequências positivas

- Rotas e erros têm direção conhecida antes de iniciar a API.
- O comportamento de consulta e o domínio continuam separáveis para testes offline.
- A interface pode evoluir junto ao produto, inclusive com diferentes verificações de saúde quando justificadas.

## Consequências negativas e trade-offs

- FastAPI adicionará dependências estruturais de runtime e manutenção; OpenAPI não garante que os dados ou afirmações tenham suporte semântico.
- `/v1` e os códigos públicos exigem política de compatibilidade quando houver consumidores.
- Problem Details exige tradução e testes consistentes; não expor detalhes internos por conveniência.
- A documentação interativa offline pode exigir empacotar e atualizar arquivos adicionais.

## Riscos

- **Compatibilidade ainda não demonstrada:** antes de adicionar dependências, verificar FastAPI, servidor ASGI e transitivas com Python 3.14.8 em ambiente isolado, escolher versões e registrar evidência e lockfile. Se a escolha se mostrar inviável ou exigir mudança arquitetural relevante, registrar alternativas e levar a decisão ao PO.
- **Limites de inicialização e consulta:** definir e testar leitura local, erros e limites durante o refinamento, sem inferir requisitos não aprovados. A aplicação ainda não foi testada como servidor.
- **Validação duplicada:** não deixar coerções ou modelos de transporte enfraquecerem a validação existente; testar a fronteira e a tradução dos erros conforme a origem dos dados.
- **Evolução para produto:** revisitar saúde, segurança, suporte, compatibilidade e custos quando houver necessidades e evidências; não antecipar infraestrutura de produção como requisito atual.

## Referências

- [STORY-011](../../roadmap/stories/STORY-011.yaml), [STORY-012](../../roadmap/stories/STORY-012.yaml), [HANDOFF-011](../../agents/handoffs/HANDOFF-011.yaml) e [Q-005](../decisions/open-questions.md).
- [RFC 9110 — semântica HTTP](https://www.rfc-editor.org/rfc/rfc9110.html), [RFC 9457 — Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html).
- [FastAPI — recursos](https://fastapi.tiangolo.com/features/), [concorrência](https://fastapi.tiangolo.com/async/) e [documentação com ativos locais](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/).
- [Starlette](https://starlette.dev/) e [decisões de design do Flask](https://flask.palletsprojects.com/en/stable/design/).
