# ADR-0006 — Integração local da explicação restrita

## Status e autorização

`accepted` em 2026-11-02 para a primeira vertical. O PO solicitou concluir a STORY-021 com o Qwen já testado, limite de 512 tokens e teste real; antes havia autorizado Colibri e o timeout de até 300 segundos. A proposta anterior deste ADR era experimental e consta no histórico Git. Esta decisão complementa os ADRs 0002 e 0004, sem substituí-los. Não declara o modelo universalmente adequado nem aprova deploy remoto.

## Contexto e evidências

A política aceita exige frases canônicas e verificação independente antes de exibi-las. OLMoE falhou no formato em duas chamadas. Qwen3-Coder-30B-A3B int4, executado por Colibri, produziu seleções válidas em seis chamadas controladas das três fixtures, em cerca de 101–107 s e pico RSS reportado de aproximadamente 6,25 GiB. Os testes são poucos e não demonstram confiabilidade geral; resultados e limites estão na [avaliação](../decisions/story-021-avaliacao.md). O PO escolheu 512 tokens como teto; as amostras disponíveis não demonstram que esse teto seja mais rápido.

## Alternativas

1. **Escolhida para esta vertical:** Colibri local, servidor iniciado pelo operador em loopback e protocolo HTTP compatível com `/v1/chat/completions`; cliente assíncrono da biblioteca padrão, sem SDK ou dependência estrutural adicional. A resposta é uma seleção de IDs; o núcleo verifica e monta as frases. O modelo é candidato escolhido para este recorte, não garantia de qualidade futura.
2. CLI por requisição: exigiria gerenciar carga, ciclo de vida e parsing; o motor Qwen da versão testada não oferece `coli run`, conforme seu registro de famílias.
3. Somente modo determinístico: reproduzível e disponível como fallback, mas não atende à explicação local exigida nesta vertical.

## Decisão e limites

- Usar Qwen3-Coder-30B-A3B int4 da revisão `d839110a17d31b4e6fa9f3d973b751f779b6b9c6` e Colibri `e0db083cdc9e563e0766cc6fc661ef23c32298e0` na demonstração, sem pesos no repositório. Servidor manual e cliente restrito a `127.0.0.1`, sem proxy, redirecionamento, TLS externo ou ferramentas.
- Pedir no máximo 512 tokens, temperatura zero, resposta não streaming e até 300 s totais para a chamada. Limitar corpo da resposta a 64 KiB, sem repetição automática. Servidor é iniciado com `--max-queue 0` e uma inferência por vez; concorrência adicional no processo da API devolve fallback imediato.
- A demonstração usa contexto 2048, cache de 32 especialistas por camada e limite de processo `MemoryMax=9G`, `MemorySwapMax=1G` e `CPUQuota=400%`, como nos experimentos. O `--cap` controla cache nesse motor; `--ram` não é limite de RSS. Não iniciar o serviço automaticamente na API.
- Limites locais de transporte: corpo de entrada HTTP de até 256 KiB; para explicação, até 16 observações e prompt de até 4096 bytes. Dados classificáveis maiores continuam com resultado determinístico e limitação de explicação indisponível. Esses limites não mudam o contrato do núcleo.
- Entrada inválida e insuficiente nunca chamam o modelo. Falha, indisponibilidade, timeout, resposta malformada, truncada, IDs inválidos ou referências inválidas preservam o resultado básico, sem texto rejeitado. O operador controla o servidor; o `/health` da API não depende dele.

## Consequências e riscos

Um timeout do cliente encerra sua espera e conexão, mas **não prova o cancelamento da inferência no Colibri**. O servidor com fila zero rejeita outras requisições enquanto estiver ocupado; parar o processo é responsabilidade do operador. Limites de recursos são da demonstração local, não garantias para outras máquinas. Referências resolúveis não provam apoio semântico e os resultados das fixtures não demonstram confiabilidade geral. Nenhum serviço pago, acesso remoto, remediação, publicação, tag ou aprovação de release decorre desta decisão.

## Referências

[Requisitos](../REQUIREMENTS.md), [ADR-0002](0002-llm-local-primeira-vertical.md), [ADR-0004](0004-api-local-contratos-http.md), [questões abertas](../decisions/open-questions.md), [STORY-021](../../roadmap/stories/STORY-021.yaml), [avaliação](../decisions/story-021-avaliacao.md).
