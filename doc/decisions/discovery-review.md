# Revisão da descoberta — gate da primeira implementação

## Estado

**Descoberta aceita pelo PO em 2026-10-30; próxima etapa de setup autorizada.** A [STORY-004](../../roadmap/stories/STORY-004.yaml) exige revisão independente e validação explícita do Product Owner (PO) do escopo, critérios e cenários. Em 2026-10-30, o PO aceitou escopo, cenários e requisitos, relatou ter executado os scripts e revisado os arquivos como desenvolvedor, e pediu alteração para Python 3.14; o PO confirmou que a proposta e os cenários atendem ao esperado para iniciar. Evidência em [HANDOFF-004](../../agents/handoffs/HANDOFF-004.yaml). A verificação inicial do executor não constitui revisão independente; a revisão do PO como desenvolvedor é relatada separadamente no handoff.

## Artefatos e fluxo para revisão

1. [Produto](../PRODUCT.md): pessoa fornece incidente sintético; regras previstas avaliam sinais e referências; LLM local explica o resultado; falha ou rejeição preserva saída básica; pessoa decide o próximo passo. Não há remediação ou consulta externa na primeira vertical.
2. [Cenários e reprodução](../INCIDENTS.md): três fixtures JSON locais, com janela, sinais, evidências e limitações. As entradas são reproduzíveis a partir dos arquivos; o procedimento usa Python 3 sem rede ou credenciais.
3. [Requisitos propostos](../REQUIREMENTS.md): regras sintéticas com faixas, janelas, política de dados faltantes, critérios de falha e explicação restrita. A tabela de exemplos reproduz `media`, `alta` e `alta`. Os critérios foram aceitos pelo PO em 2026-10-30.
4. [ADR-0001](../adr/0001-monolito-modular-baseline-deterministico.md) mantém monolito modular e núcleo determinístico; a exclusão de LLM na primeira vertical foi parcialmente substituída pelo [ADR-0002](../adr/0002-llm-local-primeira-vertical.md). O ADR-0002 aceita LLM local para explicação, verificação independente de referências e fallback básico. Nenhum modelo definitivo foi aceito.

## Decisões aceitas e pendência do gate

- **Q-002 — limiares e informação parcial:** PO aceitou a tabela sintética de [requisitos](../REQUIREMENTS.md), janelas de 10 minutos e sinais de 5 minutos, maior severidade observada e classificação parcial com limitações. Os valores são arbitrários para testes e não estabelecem política de produção.
- **Q-003 — falhas e explicação:** PO aceitou os critérios e casos de falha, incluindo `insuficiente`, `entrada_invalida` e fallback. A proposta faz o LLM selecionar frases canônicas, que o núcleo monta e verifica. Isso limita a variedade de explicações, mas reduz o risco de apresentar afirmações novas sem apoio. Uma alternativa é permitir texto livre e desenvolver avaliação e verificação de suporte semântico mais abrangentes; é mais flexível e sua confiabilidade não decorre apenas da existência das referências. Em ambos os casos, o ADR-0002 exige saída básica em falha ou rejeição.
- **Q-015 — gate:** o PO aceitou o conjunto, informou ter revisado arquivos e executado scripts e confirmou que cenários e proposta atendem ao início; revisão registrada no handoff.

## Evidências e pendências por critério

| Critério | Evidência disponível | Estado |
|---|---|---|
| AC-01: outra pessoa ou agente reproduz e valida o fluxo documentado | Procedimentos e dados em [INCIDENTS](../INCIDENTS.md); verificação do executor registrada no handoff | PO, como desenvolvedor, relatou executar os scripts e revisar os arquivos; confirmou que cenários e proposta atendem ao esperado. As saídas dos comandos não foram fornecidas; fluxo abaixo foi redigido pelo executor e validado pelo PO, que não o reexplicou. |
| AC-02: sem conflitos ou bloqueios | Correspondência documentada na tabela de [requisitos](../REQUIREMENTS.md); Q-002/Q-003 identificadas | Decisões aceitas pelo PO; ele relatou não ter outras observações além da versão do Python, atualizada para 3.14. |
| AC-03: ADRs revisados | Leitura e relação entre ADR-0001/0002 acima, pelo executor | Preparado; nenhuma mudança incompatível proposta como aceita. |
| AC-04: validação do PO | Aprovações anteriores de produto e STORY-002 nos respectivos handoffs | PO aceitou o conjunto da descoberta em 2026-10-30, registrado no handoff. |
| AC-05: continuidade para setup | [STORY-010](../../roadmap/stories/STORY-010.yaml) e Q-004 em [questões abertas](open-questions.md) | Gate aceito; STORY-010 é a próxima, após preparação dos contratos. |

## Continuidade após o gate

A STORY-010 precisa de refinamento, contrato e decisão sobre versões Python, gerenciador, lint, type checker e CI. Escolhas estruturais exigem ADR e aprovação do PO antes da adoção; [ADR-0003](../adr/0003-ambiente-python-qualidade.md) foi aceito após teste isolado com Python 3.14. A aceitação da descoberta não escolhe modelo LLM definitivo, banco, API ou dependências de setup. Os detalhes do modelo e sua avaliação seguem nas questões Q-007 e Q-016.

## Registro do ajuste de AC-01

O texto original pedia que outro desenvolvedor explicasse o fluxo. Após revisar os arquivos e relatar a execução dos scripts, o PO, também desenvolvedor, confirmou que a proposta e os cenários atendem ao esperado para iniciar, sem reexplicar o fluxo em suas palavras. Em respeito ao aceite e ao pedido de continuidade, o critério foi ajustado para validação do fluxo já documentado. O relatório não atribui ao PO uma explicação ou saídas de comandos que ele não forneceu. O fluxo validado é o item 1 desta página; a execução das regras por um motor continua futura.
