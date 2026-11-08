# STORY-050 — comparação local de coordenação

## Protocolo anterior aos testes

Comparar A, a rota real `POST /v1/investigations` exercitada em processo pelo TestClient, com B, protótipo separado em `scripts/workflow_050.py`. Ambos usam as mesmas funções de triagem, catálogo canônico e verificação e recebem seletores simulados equivalentes. Nenhuma chamada real de modelo ou rede está autorizada. Os casos usam fixtures sintéticas de INC-001 e entrada deliberadamente alterada; não são teste representativo ou benchmark de modelo.

Cenários congelados: sucesso; unidade inválida; ausência de sinais; timeout simulado como `ModelUnavailable` conforme a fronteira da vertical; indisponibilidade simulada; falha intermediária `ModelRejected`; referência inexistente; resposta livre adicional; mais de 16 observações; erro interno inesperado. Comparar HTTP e conteúdo sanitizado para saídas normais e classificação `erro_interno` para erro inesperado; verificar que entrada inválida e insuficiência não chamam o seletor. No protótipo, verificar transições, limite fixo de passos e uma chamada de seleção. Os testes usam um cliente ASGI em memória; não exercitam transporte do Colibri.

Inspecionar separadamente a complexidade estrutural e a capacidade de entendimento dos caminhos; não interpretar contagem de linhas como produtividade ou vantagem. Verificar que estado em memória do protótipo é observável no retorno; a rota atual devolve triagem e estado da explicação, não um registro de cada transição. Nenhum cenário prova persistência, retomada após reinício, cancelamento do servidor, concorrência ou qualidade semântica de LLM. A comparação não será extrapolada para recuperação ou análise descritiva integradas: esses componentes existem separadamente e a rota atual não os chama.

A primeira vertical é o baseline real; B é experimento descartável e não foi incorporado à API. A decisão será documentada em ADR com estado proporcional à autoridade disponível. A restrição de ferramentas significa que o protótipo não fornece qualquer ferramenta de modificação; a ausência de chamada de ferramentas nos testes não comprova sandbox geral de uma função arbitrária injetada. Os resultados observados serão registrados após a execução.

## Estrutura efetivamente comparada

Na rota atual, a API limita o corpo e decodifica JSON; `triage_incident` valida e classifica, produzindo a resposta determinística. Se houver dados suficientes e até 16 observações, a rota cria frases canônicas, chama o seletor Colibri e verifica a seleção e seus vínculos. Se o seletor estiver indisponível ou retornar seleção rejeitada, conserva triagem e informa o estado da explicação. A recuperação lexical, a análise descritiva curada e seus mocks são funções separadas; a rota não as conecta. O timeout do Colibri é tratado como indisponibilidade, e o cliente não comprova cancelamento do servidor.

B é uma máquina de estados em memória (`triagem → selecao → verificacao → fim`), com saltos condicionais para `fim`, no máximo três etapas e uma chamada do seletor. Seu objeto retorna estágio e transições, mas não tem persistência, replay, deadline próprio, cancelamento de provedor ou integração HTTP. Para isolar a diferença de coordenação, B reutiliza núcleo, verificador e auxiliares de formatação da API; por isso os testes não são implementações independentes de verificação. Ele recebe um callable de teste confiável; não oferece API para ferramentas ou comandos e não é sandbox para callables arbitrários.

## Resultados observados

Executado `uv run --offline --locked --no-sync pytest -q tests/evaluation/test_workflow_050.py`: **12 testes passaram**. Em dez cenários parametrizados, a rota e o protótipo apresentaram o mesmo código e corpo, exceto o erro interno, comparado pelo código e sanitização. São eles: sucesso, unidade inválida, insuficiência, timeout simulado, indisponibilidade simulada, rejeição de etapa, ID de frase inexistente, texto livre extra, excesso de observações e erro inesperado. Timeout e indisponibilidade foram injetados como a mesma exceção `ModelUnavailable`; não foi medido timeout real ou cancelamento. Um teste adicional adulterou a referência de evidência no catálogo e confirmou rejeição em ambos; outro verificou no protótipo a parada por limite de passos, antes do seletor.

Nos cenários, seleção não foi chamada para entrada inválida, insuficiência ou excesso de observações; nos demais houve no máximo uma chamada. No sucesso, B expôs `triagem, selecao, verificacao, fim`. Não foi implementada instrumentação equivalente por etapa em A; seu retorno expõe estado de explicação e resultado de triagem. A equivalência é de saídas controladas deste recorte, não uma medida de qualidade semântica, inferência real ou robustez geral. A arquitetura do protótipo reutiliza o núcleo e partes da API, portanto o resultado não é validação independente da correção dessas funções.

| Aspecto | A: vertical atual | B: protótipo explícito |
|---|---|---|
| Simplicidade/manutenção | Fluxo direto já implementado na rota. | Acrescenta objeto de estado, despachante, transições e testes; duplica parte da coordenação e depende de auxiliares privados da API. |
| Estado e observabilidade | Resposta expõe triagem e estado da explicação; não registra transições. | Transições e número de chamadas visíveis no objeto em memória; não há rastreamento durável. |
| Falhas e fallback | Tratamento existente na rota, exercitado com mock. | Tratamento explícito reproduziu as saídas dos cenários testados; limite do protótipo gera erro próprio e não corresponde a contrato HTTP existente. |
| Retomada | Não há retomada por etapa demonstrada. | Não há checkpoint, replay ou retomada após reinício; o estado em memória não comprova essas capacidades. |
| Qualidade | Resultados determinísticos e seleção simulada no recorte. | Mesmos resultados observados no recorte; não demonstra melhora de análise ou verificação. |
| Operação | Dependências atuais e operação já documentada. | Nenhuma dependência nova no experimento; custo adicional de implementação/manutenção não foi quantificado. |

Recomendação para este recorte: **manter a vertical existente** e não integrar o protótipo. Ele torna o percurso visível em memória, mas introduz duplicação e não demonstra retomada nem ganho de qualidade. Reavaliar com necessidade concreta de estados duráveis, novos caminhos efetivamente integrados ou dificuldade observada de operação, mediante desenho e aprovação quando necessários. A recomendação não impede trabalho futuro e não conclui EPIC-005. ADR, limitações e autoridade estão em [ADR-0007](../adr/0007-comparacao-workflow.md).
