# ADR-0008 — Manter o baseline após avaliação exploratória de documentos ricos

## Status e autoridade

`accepted` para a decisão técnica limitada de **manter o baseline lexical existente**, já adotado no projeto, sem integração ou nova dependência. O PO autorizou o encerramento da STORY-060/EPIC-006 após os aceites individuais dos incrementos; a revisão do PR permanece pendente. Essa solicitação não é apresentada como revisão humana prévia deste ADR. A decisão preserva os ADRs 0001 e 0002; não os substitui, nem autoriza arquitetura nova.

## Data e contexto

2026-11-12. A STORY-061 produziu e teve aceito o corpus sintético RICH-01; STORY-062 e STORY-063 avaliaram extração, chunking e recuperação localmente e receberam aceite exploratório do PO. Os resultados e falhas estão nos [relatórios de ingestão](../architecture/rich-document-ingestion-results.md) e [recuperação](../architecture/rich-document-retrieval-results.md). O pipeline lexical existente trabalha com corpus próprio; o adaptador experimental foi isolado, preservou equivalência no corpus C1 e não foi integrado à aplicação.

## Alternativas

1. Manter o baseline lexical existente e os experimentos isolados; sem custo de implantação ou dependência estrutural nova.
2. Adotar um extrator estruturado e transportar metadados como parte do produto: C1 preservou melhor relações tabulares no corpus, mas persistem ambiguidade de colunas e ausência de metadados de tabela e seção nos chunks. Integração, licenças, manutenção e custo operacional não foram avaliados para produção.
3. Adotar busca vetorial, híbrida ou framework de ingestão: não testados nos estudos; dependências, infraestrutura e operação não foram medidas. Exigiriam proposta, evidências, ADR e autorização humana antes da implementação.

## Decisão e justificativa

Manter o baseline já existente sem promover o adaptador experimental ou selecionar um extrator para produção. Não há evidência suficiente de benefício geral ou preparo operacional para mudança estrutural. Em RICH-01, C1 preservou melhor as evidências tabulares, mas os rankings B1/C1 foram idênticos em IDs, scores e ordem; não houve demonstração de melhoria do algoritmo lexical ou do chunking. O escopo da decisão é conservar o que já existe, não afirmar que o baseline suporte PDFs arbitrários ou RAG completo.

## Consequências e riscos

A operação e dependências atuais permanecem; o baseline não incorpora documentos ricos automaticamente. O corpus sintético é pequeno e conhecido do executor, não representa teste cego ou independente. As páginas curtas não exercitaram divisão efetiva, sobreposição ou truncamento real; as seções dos chunks não foram extraídas. Citações de página são tecnicamente resolvíveis, mas suporte semântico requer avaliação própria; Q06/Q07 têm colunas ambíguas, Q10 exige duas páginas e Q12/Q13 não provocaram abstenção lexical.

O estudo não mede escalabilidade, inferência real, respostas de LLM, custo de produção ou qualidade geral de RAG. Reavaliar diante de novos requisitos ou evidências, com protocolo, versões, recursos e autorização apropriados. A [proposta futura](../architecture/rich-document-next-increment-proposal.md) é opcional e não está implementada ou autorizada.

## Referências

[STORY-060](../../roadmap/stories/STORY-060.yaml), [consolidação de gates](../architecture/epic-006-closure.md), [aceite 061](../decisions/story-061-aceite.md), [aceite 062](../decisions/story-062-aceite.md), [aceite 063](../decisions/story-063-aceite.md), [ADR-0001](0001-monolito-modular-baseline-deterministico.md) e [ADR-0002](0002-llm-local-primeira-vertical.md).
