# Plano do estudo de fontes e avaliação própria

## Estado e decisão do PO

Em 2026-11-03, o PO aprovou a direção de estudar **Prometheus Operator + seleção do GitLab como fontes documentais, com avaliação própria revisada pelo PO e pelo executor**. Solicitou catalogar a [SPIKE-030](../../roadmap/stories/SPIKE-030.yaml) no [EPIC-003](../../roadmap/epics/EPIC-003.yaml), como pré-requisito explícito das STORY-030 e STORY-031, e preparar a continuidade em outra sessão.

Esta entrega prepara o contrato do estudo: SPIKE-030 `ready`, SPEC-029 `ready`, ACT-029 `pending`. Não é aceite dos documentos individuais, dos rótulos, de metas de qualidade ou do protocolo final. O estudo e sua revisão ainda não ocorreram. As relações são explícitas pelos IDs; SPEC/ACT/HANDOFF-029 foram alocados para deixar os números 030 e 031 livres para as histórias posteriores.

## Como se encaixa no AegisOps

- STORY-021 permanece com severidade e evidências determinísticas e Qwen selecionando IDs de frases canônicas verificadas. Runbooks não são inseridos nessa explicação nem treinam o modelo.
- SPIKE-030 estuda fontes, aplicabilidade e desenho de avaliação; entrega relatório, manifesto candidato e revisão do PO.
- STORY-030 prepara corpus Markdown e dataset rotulado a partir das decisões do estudo.
- STORY-031 implementa e mede busca lexical. A análise ampliada com LLM pertence a etapas posteriores e requer seus contratos.

Uma observação do incidente é evidência de um sinal; um runbook é conhecimento sobre verificações possíveis. Recuperar um documento não comprova sua hipótese causal e não autoriza executar seus comandos. O estudo não muda os limites de 512 tokens ou o protocolo da primeira vertical.

## Pesquisa exploratória que antecede o estudo

As observações abaixo foram obtidas na pesquisa de 2026-11-03. São pontos de partida a revalidar, não auditoria completa, benchmark executado ou aprovação final de uso. Links externos mudam; registrar uma revisão ou versão para cada amostra durante o estudo.

| Fonte primária | Observação exploratória | Uso candidato e limites |
|---|---|---|
| [Prometheus Operator Runbooks](https://github.com/prometheus-operator/runbooks) e [licença](https://github.com/prometheus-operator/runbooks/blob/main/LICENSE) | A árvore consultada em `a685d14cf5128bb30e2bf935c3983decd772d885` continha 108 arquivos Markdown de runbook, excluídos índices; licença Apache-2.0. | Fonte inicial de estrutura e documentos curtos; foco em Kubernetes e monitoramento, com lacunas em alguns procedimentos. |
| [GitLab Runbooks](https://gitlab.com/gitlab-com/runbooks) e [licença](https://gitlab.com/gitlab-com/runbooks/-/blob/master/LICENSE) | Documentos públicos e licença MIT indicada pelo projeto. | Selecionar trechos de diagnóstico de aplicações, bancos e dependências, sem assumir infraestrutura, painéis ou permissões do GitLab. |
| [Awesome Prometheus Alerts](https://github.com/samber/awesome-prometheus-alerts/blob/master/LICENSE) | Conteúdo de alertas CC BY 4.0; código do site MIT. | Vocabulário e distratores; coleção de regras não substitui corpus de runbooks. |
| [Synthetic Incident Search Benchmark](https://huggingface.co/datasets/trentdoney/synthetic-incident-search-benchmark) | Leitura dos JSONL encontrou 12 incidentes, 18 consultas e 18 rótulos, todos com algum incidente relevante; cartão CC BY 4.0. | Exemplo pequeno de consultas e negativos difíceis; recupera incidentes históricos e não cobre ausência nas amostras lidas. |
| [Enterprise ITSM](https://github.com/guneeshvats/enterprise-itsm-benchmark) | Projeto MIT anuncia 1.000 incidentes e 2.280 artigos. O [arquivo de rótulos](https://github.com/guneeshvats/enterprise-itsm-benchmark/blob/main/kb_and_relationships/ground_truth/_kb_retrieval_gt.json) examinado tinha 393 registros, 273 positivos e 120 sem artigo. O [relatório do autor](https://github.com/guneeshvats/enterprise-itsm-benchmark/blob/main/kb_and_relationships/validation/_validation_report.json) aponta artigo ausente `KB0100152` e distratores possivelmente fáceis. | Estudar ideias e eventual subconjunto auditado; divergências impedem adoção integral automática. Contagens de metadados não substituem inspeção dos registros. |
| [TechQA oficial](https://github.com/IBM/techqa) e [distribuição indicada](https://huggingface.co/datasets/PrimeQA/TechQA) | Treino e desenvolvimento indicados pelo repositório; distribuição com cerca de 2,96 GB e cartão Apache-2.0; leaderboard encerrado. | Referência de suporte técnico e perguntas sem resposta em candidatos; domínio IBM distante dos cenários atuais. Pacote completo e rótulos originais de teste não foram inspecionados. |
| [BEIR](https://github.com/beir-cellar/beir) | Separa corpus, consultas e julgamentos de relevância e documenta métricas de recuperação. | Referência de método, sem adotar biblioteca, embeddings ou dependências agora. |

RCAEval, ITBench e AIOpsLab foram identificados como fontes possíveis para telemetria e avaliação operacional em etapas posteriores, não como corpus inicial ou protocolo aceito deste estudo.

## Perguntas que o estudo deve resolver

1. Quais amostras ajudam a investigar latência, HTTP 5xx, utilização de CPU e memória nos três cenários de [INCIDENTS](../INCIDENTS.md), considerando os contratos vigentes de [REQUIREMENTS](../REQUIREMENTS.md)?
2. Quais documentos só parecem relacionados, mas exigem outro componente, outra infraestrutura ou sinais ausentes?
3. Qual recorte permite revisão humana e reprodução local sem credenciais, e quais licenças, atribuições e adaptações se aplicam ao material selecionado?
4. Quais consultas são representativas e como registrar relevância, ausência e desacordo entre revisores antes de medir ranking?
5. Como separar idioma, paráfrases e traduções para não confundir falha lexical com falta de conteúdo nem contaminar desenvolvimento e teste?

Exemplos para análise: [CPUThrottlingHigh](https://github.com/prometheus-operator/runbooks/blob/main/content/runbooks/kubernetes/CPUThrottlingHigh.md) não é equivalente a utilização elevada de CPU; [KubeMemoryOvercommit](https://github.com/prometheus-operator/runbooks/blob/main/content/runbooks/kubernetes/KubeMemoryOvercommit.md) trata de capacidade do cluster, não do percentual de memória de um serviço. [KubeClientErrors](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubeclienterrors/) é específico de clientes da API Kubernetes. Essas diferenças são candidatas a negativos difíceis, sujeitos a revisão.

## Proposta a desenvolver e revisar

O estudo deve propor um manifesto com origem, caminho, revisão ou versão, data de consulta, licença declarada, idioma, atribuição, adaptação prevista e justificativa de inclusão ou exclusão. Quando houver trecho, preservar também sua localização e condições de aplicação.

Para a avaliação própria, propor exemplos com `query_id`, consulta, idioma, cenário, documentos e trechos esperados, negativos difíceis, justificativa e registro de revisão. Relevância pode admitir mais de um documento. Ausência é relativa a uma versão do corpus e deve ser explícita; não equivale a incidente saudável, sem solução ou sem evidência.

Separar grupos de paráfrases e traduções entre desenvolvimento e teste. Propor Recall@3/5 e posição do primeiro relevante para consultas positivas, e medir separadamente retorno indevido e abstenção correta para consultas sem documento. Explicitar denominadores, exclusões e resolução de origem/versão. Esses são candidatos de método, sem meta numérica de aceite ou resultado de desempenho já estabelecido.

As sugestões iniciais de 8–12 runbooks centrais e 60–100 consultas são apenas estimativas para discussão. O tamanho final, os idiomas, o equilíbrio entre cenários e a quantidade de distratores precisam de justificativa e revisão; não há obrigação de atingir esses números no estudo.

## Entrega e gate

Entregas futuras previstas: `doc/research/SPIKE-030.md` e `doc/research/spike-030-fontes.yaml`, além da atualização do [HANDOFF-029](../../agents/handoffs/HANDOFF-029.yaml). Não criar corpus ou dataset final em `datasets/` nesta spike.

O executor prepara evidências e propõe rótulos. O PO revisa amostras, protocolo e decisões; registrar concordâncias, divergências, alterações e pendências. O LLM não é juiz final dos rótulos. Somente depois dessa revisão e dos critérios atendidos a SPIKE-030 pode ficar `done`; isso libera dependências, sem iniciar automaticamente as histórias seguintes.

A [Q-020](open-questions.md) guarda as decisões pendentes. O [prompt da próxima sessão](spike-030-proxima-sessao.md) contém a sequência de continuidade e a verificação da base local, cujo fechamento do EPIC-002 ainda não foi publicado na remota no momento da preparação.
