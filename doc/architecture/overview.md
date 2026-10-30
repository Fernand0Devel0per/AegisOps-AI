# Arquitetura e análise do plano

Fonte: [plano original](../../AegisOps_AI_Plano_do_Zero.md), seções 1–12. Data da análise: 2026-10-30. Nada nesta visão indica implementação da aplicação.

## Propósito e fronteiras

O produto proposto ajuda uma pessoa a investigar degradação correlacionando sinais operacionais e runbooks. A saída separa observações, hipóteses, evidências, recomendações e limitações. Inicialmente tudo é local, sintético e somente de leitura. O portfólio deve demonstrar engenharia e aprendizado com resultados medidos.

Há dois recortes distintos: a primeira vertical determinística (Etapas 0–2, candidata a `v0.1.0`) e o MVP ampliado (runbooks e análise opcional com LLM, testes, CI e telemetria progressiva). Não é preciso incluir o MVP ampliado na primeira release.

## Visão alvo e incremento inicial

```text
Entrada autorizada → API/CLI → workflow simples
    → triagem de sinais
    → consulta de runbooks
    → análise / hipóteses (LLM opcional, posteriormente)
    → validador determinístico de evidências e políticas
    → relatório humano + histórico/status quando necessário

Telemetria do workflow → OpenTelemetry → stack de observabilidade posterior
Sinais investigados → fonte sintética inicialmente, demo instrumentada depois
```

Esses são papéis lógicos, não serviços separados. A primeira implementação deve conter apenas os componentes necessários para consultar incidentes e depois classificá-los. Não se exige um framework de agentes para um pipeline simples. O [ADR-0001](../adr/0001-monolito-modular-baseline-deterministico.md) registra o ponto de partida explícito do plano.

`Incident`, `Signal`, `Evidence`, `Hypothesis`, `Investigation` e `Recommendation` são entidades conceituais candidatas. Esquemas e fronteiras definitivos não foram aprovados. A Etapa 0 deve definir entradas/saídas mínimas, unidades, períodos e resultados esperados, antes da modelagem Python.

## Tecnologias e momento de decisão

| Necessidade | Direção do plano | Gate |
|---|---|---|
| Linguagem e API | Python; FastAPI/Pydantic preferenciais | Etapa 1; ADR antes de dependências estruturais |
| Qualidade | Pytest, Ruff, type checker; `uv` ou equivalente | Setup mínimo, sem banco/fila |
| Conhecimento | Markdown e busca lexical | Baseline e dataset rotulado antes de embeddings |
| Análise probabilística | Ollama ou provedor com chave por ambiente | Baseline determinístico, mock offline e critérios de avaliação |
| Estado orquestrado | LangGraph ou implementação simples | Demonstrar necessidade de branches/checkpoints/retomada |
| RAG rico | Docling, embeddings, FAISS/pgvector | Documentos autorizados; comparar com baseline, medir Recall@k/MRR quando adequados |
| Durabilidade/concorrência | PostgreSQL; workers/broker somente se necessários | Contratos de idempotência e recuperação; carga e falhas medidas |
| Operação | OTel e stack de observabilidade; Compose; depois Kubernetes/GitOps | API local estável antes de containers; deploy reproduzível antes de GitOps; capacidade medida antes de HPA/KEDA |
| Conectores remotos | OIDC/JWT, permissões por ferramenta | Antes de qualquer conexão real; fora do MVP inicial |

Não foram pesquisadas versões atuais nem testada a compatibilidade dessas candidatas nesta entrega documental. A decisão de instalação deve validar versões na etapa correspondente.

## Viabilidade, dependências e tensões

O recorte inicial é viável sem serviço pago: incidentes sintéticos, regras determinísticas e execução local permitem testes reproduzíveis. A visão completa tem custo de estudo e operação considerável; manter etapas e gates evita transformar a lista de ferramentas em escopo obrigatório.

| Observação no plano | Tratamento no roadmap |
|---|---|
| Etapa 1 apresenta API antes do motor da Etapa 2; primeira release exige os dois | Primeira API consulta incidentes; integração da triagem é entrega posterior na Etapa 2 |
| CI está na Etapa 1 e também no golden path da Etapa 9 | CI mínimo na Etapa 1; imagens, análise ampliada e deploy na Etapa 9 |
| Compose é sugerido após API e aparece na Etapa 9 | Permitido após API se necessário e aprovado; golden path consolidado na Etapa 9, sem dependência antecipada |
| Segurança aparece como Etapa 10 | Princípios de segurança valem desde o início; Etapa 10 consolida testes adversariais e documentação |
| Métricas/telemetria estão no MVP, stack completa na Etapa 7 | Contratos e observabilidade progressivos; não afirmar MVP ampliado completo antes de demonstrar telemetria |
| Orquestração, vetores e brokers são condicionais | Épicos de evolução exigem comparação; concluir avaliação pode recomendar manter a solução simples |
| Arquitetura de microsserviços aparece no problema | O AegisOps começa monolito; o serviço investigado pode ser distribuído sem tornar a plataforma distribuída |

A dependência cronológica conservadora entre épicos é planejamento, não acoplamento obrigatório entre tecnologias. Depois do baseline, dependências podem ser refinadas para avaliar RAG ou observabilidade sem adotar LangGraph. O objetivo educacional e a validação do PO permanecem gates.

## Riscos e incógnitas

- Severidade, limiares, unidade, janela temporal e sinal insuficiente ainda não têm contrato; descobri-los na Etapa 0, sem tratar exemplos sintéticos como valores de produção.
- Qualidade de hipóteses e retrieval exige dataset e revisão, não apenas uma demo bem sucedida.
- Modelos locais podem exigir recursos não disponíveis; o modo offline determinístico/mock deve continuar suficiente para reprodução.
- Documentos podem conter instruções maliciosas; referências existentes não garantem que sustentem uma alegação. Validar existência é uma barreira necessária, não prova de causalidade.
- PostgreSQL, brokers, Kubernetes e GitOps adicionam operação. Introduzir somente com necessidade, alternativas e custo registrados em ADR.
- O pedido atual muda o modo de colaboração do plano (mentoria para execução por agentes); a mudança está explicitada em [bootstrap-scope.md](../decisions/bootstrap-scope.md).

As decisões pendentes, responsáveis e etapas de resolução estão em [open-questions.md](../decisions/open-questions.md).
