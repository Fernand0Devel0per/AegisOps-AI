# Pendências, riscos e participação humana

Estado em 2026-10-31. Itens futuros não bloqueiam a preparação documental nem a redação inicial de produto. Hipóteses e candidatas não são decisões aceitas.

| ID | Lacuna / decisão | Responsável e momento | Impacto / próximo passo |
|---|---|---|---|
| Q-001 | Quem usa a primeira vertical e qual decisão toma? | PO respondeu na revisão da STORY-001, em 2026-10-30 | Desenvolvedores, profissionais de DevOps e outros responsáveis pela checagem; PO concordou com a decisão de priorizar o incidente e escolher os sinais a examinar. Proposta da STORY-001 aceita pelo PO em 2026-10-30; evidência em [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml) |
| Q-002 | Sinais, unidades, intervalos, limiares e semântica de severidade | Agente de requisitos + PO; STORY-002/003 | PO aceitou em 2026-10-30 os limiares sintéticos, janelas e política parcial de [REQUIREMENTS](../REQUIREMENTS.md); não são números operacionais. Evidência em [HANDOFF-004](../../agents/handoffs/HANDOFF-004.yaml) |
| Q-003 | Cinco critérios observáveis, três falhas e insuficiência de evidência | Agente + PO; STORY-003 | PO aceitou em 2026-10-30 os critérios e falhas de [REQUIREMENTS](../REQUIREMENTS.md), inclusive explicação restrita; evidência em [HANDOFF-004](../../agents/handoffs/HANDOFF-004.yaml) |
| Q-004 | Python, versões compatíveis, gerenciador e type checker | Agente de setup propõe; PO decide ADR estrutural antes da STORY-010 | PO aprovou Python 3.14.8 e ferramentas do [ADR-0003](../adr/0003-ambiente-python-qualidade.md) em 2026-10-30 após teste isolado; instalação limpa do projeto e CI seguem para STORY-010 |
| Q-005 | Rota/CLI mínima e contratos de erros; fluxo síncrono inicial | PO aceitou a direção da API em 2026-10-31; refinamento técnico na STORY-012 | Direções aceitas em [ADR-0004](../adr/0004-api-local-contratos-http.md): FastAPI, rotas, Problem Details e resposta na requisição. Versões, compatibilidade, servidor ASGI, detalhes de transporte e eventual CLI continuam pendentes; nenhuma API implementada. Evidência em [HANDOFF-011](../../agents/handoffs/HANDOFF-011.yaml) |
| Q-006 | Política e medidas de sucesso para hipóteses e retrieval | PO + agente de avaliação; Etapas 3–4 | Definir dataset e metas antes dos testes; medir sem fabricar resultados |
| Q-007 | Modelo local, recursos e avaliação | PO aprovou Colibri para explicação na primeira vertical; modelo definitivo pendente | Avaliar qualidade, latência, memória e licença; manter resultado básico sem credenciais ou LLM |
| Q-008 | LangGraph versus pipeline simples | Agente apresenta experimento; PO aprova adoção; Etapa 5 | Só adotar se houver ganho demonstrável; resultado válido pode manter baseline |
| Q-009 | Docling, FAISS/pgvector e busca lexical/vetorial/híbrida | Agente propõe comparação; PO decide; Etapa 6 | Documentos autorizados, métricas e análise de falhas antes de escolha |
| Q-010 | Durabilidade PostgreSQL e necessidade de worker/broker | Agente de resiliência + PO; Etapa 8 | Banco é preferencial quando necessário; Redis/RabbitMQ/fila no banco são alternativas, não adoções |
| Q-011 | Demo instrumentada; serviço opcional .NET | PO prioriza; Etapa 7 | Não é requisito obrigatório; manter sinais da demo separados da telemetria do AegisOps |
| Q-012 | Kubernetes local kind/k3d, Helm/Kustomize, GitOps e autoscaling | Agente de plataforma + PO; Etapa 9 | Começar local estável; cloud/custos só com aprovação; HPA/KEDA exigem carga e sinal útil |
| Q-013 | AuthN/AuthZ e conectores remotos | PO + agente de segurança antes de acesso real | Fora do MVP local; nenhum acesso remoto real sem escopo, permissões e ADR |
| Q-014 | Licença e reprodução documental em clones do repositório público | PO decide licença; agente adapta referências e validador | Branch enviada ao repositório público com autorização do PO; plano original segue local e ignorado. O validador deixou de exigir o plano local, mas links históricos a ele ainda podem não abrir em clones; migrar essas referências para fontes versionadas. Licença permanece indefinida. Detalhes da manutenção no [guia de validação](../standards/validation.md) |
| Q-015 | Validação da descoberta e continuação por agentes | PO; STORY-004 | PO aceitou produto, cenários e requisitos após relatar revisão e execução dos scripts; AC-01 ajustado para validar o fluxo documentado, sem atribuir explicação própria ao PO; ver [HANDOFF-004](../../agents/handoffs/HANDOFF-004.yaml) |
| Q-016 | Papel do LLM, fallback e limites de recursos na primeira vertical | Papel e fallback aprovados pelo PO em 2026-10-30; detalhes técnicos pendentes | Regras calculam severidade e verificam evidências; Colibri explica; falha mantém saída básica. Modelo definitivo, avaliação e limites seguem abertos; ver [ADR-0002](../adr/0002-llm-local-primeira-vertical.md) e [HANDOFF-001](../../agents/handoffs/HANDOFF-001.yaml) |
| Q-017 | Fechamento da STORY-012 e gate do EPIC-001 antes da STORY-020 | PO: revisar a entrega e decidir sobre o fechamento e o gate, com registro das evidências na base | PR 3 integrado, mas a base mantém STORY-012 `in_review` e EPIC-001 `in_progress`; não iniciar STORY-020 até as condições serem cumpridas. Ver [registro de bloqueio](../../agents/handoffs/STORY-020-blocked.md) |

## Riscos de execução

- **Escopo excessivo:** stack alvo mistura aprendizado e operação. Mitigação: etapas, entregas pequenas e decisões condicionais; adiar adoção sem benefício medido.
- **Confundir correlação com causa:** exigir observações e hipóteses separadas, inclusive nos resultados esperados de fixtures.
- **Prompt injection e exfiltração:** documentos e saídas de ferramentas são não confiáveis; impor políticas fora do LLM desde a introdução desse componente.
- **Portfólio impreciso:** não usar narrativa de conclusão, métricas, badges ou screenshots sem execução demonstrada.
- **Deriva documental:** alterar história/índice juntos e validar referências, dependências e evidências. Datas e comandos executados pertencem ao handoff.

Ao resolver item, registrar decisão, referência (ADR quando arquitetural), evidência e data; não apagar o histórico de uma decisão relevante.
