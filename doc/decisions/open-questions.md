# Pendências, riscos e participação humana

Estado em 2026-10-30. Itens futuros não bloqueiam a preparação documental nem a redação inicial de produto. Hipóteses e candidatas não são decisões aceitas.

| ID | Lacuna / decisão | Responsável e momento | Impacto / próximo passo |
|---|---|---|---|
| Q-001 | Quem usa a primeira vertical e qual decisão toma? | PO valida proposta do agente; STORY-001 | Redigir persona e jornada com premissas identificadas; validação antes de encerrar descoberta |
| Q-002 | Sinais, unidades, intervalos, limiares e semântica de severidade | Agente de requisitos + PO; STORY-002/003 | Não inventar números operacionais; criar cenários sintéticos explícitos e resultados esperados |
| Q-003 | Cinco critérios observáveis, três falhas e insuficiência de evidência | Agente + PO; STORY-003 | Gate para os contratos e testes da primeira implementação |
| Q-004 | Python, versões compatíveis, gerenciador e type checker | Agente de setup propõe; PO decide ADR estrutural antes da STORY-010 | Preferências do plano não equivalem a versões aprovadas; comparar custo e reprodução |
| Q-005 | Rota/CLI mínima e contratos de erros; fluxo síncrono inicial | Agente prepara SPEC da STORY-011; PO decide mudanças relevantes | Não decidir todo o modelo de investigação; sem jobs antes de necessidade |
| Q-006 | Política e medidas de sucesso para hipóteses e retrieval | PO + agente de avaliação; Etapas 3–4 | Definir dataset e metas antes dos testes; medir sem fabricar resultados |
| Q-007 | Ollama ou provedor externo; custo e hardware | PO aprova recursos/custo; Etapa 4 | Comparar qualidade/latência/custo; manter mock sem credenciais |
| Q-008 | LangGraph versus pipeline simples | Agente apresenta experimento; PO aprova adoção; Etapa 5 | Só adotar se houver ganho demonstrável; resultado válido pode manter baseline |
| Q-009 | Docling, FAISS/pgvector e busca lexical/vetorial/híbrida | Agente propõe comparação; PO decide; Etapa 6 | Documentos autorizados, métricas e análise de falhas antes de escolha |
| Q-010 | Durabilidade PostgreSQL e necessidade de worker/broker | Agente de resiliência + PO; Etapa 8 | Banco é preferencial quando necessário; Redis/RabbitMQ/fila no banco são alternativas, não adoções |
| Q-011 | Demo instrumentada; serviço opcional .NET | PO prioriza; Etapa 7 | Não é requisito obrigatório; manter sinais da demo separados da telemetria do AegisOps |
| Q-012 | Kubernetes local kind/k3d, Helm/Kustomize, GitOps e autoscaling | Agente de plataforma + PO; Etapa 9 | Começar local estável; cloud/custos só com aprovação; HPA/KEDA exigem carga e sinal útil |
| Q-013 | AuthN/AuthZ e conectores remotos | PO + agente de segurança antes de acesso real | Fora do MVP local; nenhum acesso remoto real sem escopo, permissões e ADR |
| Q-014 | Licença, nova inicialização Git, nome do remoto e publicação pública | PO antes de distribuir | Histórico Git removido por solicitação do PO; plano original local e ignorado. Migrar referências e dependência do validador para documentação pública antes de publicar |
| Q-015 | Validação da descoberta e continuação por agentes | PO; STORY-004 | Aceitar produto, cenários e requisitos; não assumir aprovação pela passagem de tempo |

## Riscos de execução

- **Escopo excessivo:** stack alvo mistura aprendizado e operação. Mitigação: etapas, entregas pequenas e decisões condicionais; adiar adoção sem benefício medido.
- **Confundir correlação com causa:** exigir observações e hipóteses separadas, inclusive nos resultados esperados de fixtures.
- **Prompt injection e exfiltração:** documentos e saídas de ferramentas são não confiáveis; impor políticas fora do LLM desde a introdução desse componente.
- **Portfólio impreciso:** não usar narrativa de conclusão, métricas, badges ou screenshots sem execução demonstrada.
- **Deriva documental:** alterar história/índice juntos e validar referências, dependências e evidências. Datas e comandos executados pertencem ao handoff.

Ao resolver item, registrar decisão, referência (ADR quando arquitetural), evidência e data; não apagar o histórico de uma decisão relevante.
