# Opções futuras — transporte de metadados de tabela

Proposta conceitual em 2026-11-12, produzida durante STORY-063. Não há escolha, implementação, teste ou adoção autorizada destas alternativas. Os chunks e resultados históricos das STORY-062/063 permanecem imutáveis. [Resultados de recuperação](rich-document-retrieval-results.md) usam somente texto e ID dos chunks existentes.

| Aspecto | A — sidecar de proveniência | B — texto enriquecido |
|---|---|---|
| Representação | Manter texto original e vincular registro separado a chunk/documento/versão/página/tabela/célula. | Acrescentar ao texto recuperável representação explícita de cabeçalho, linha, coluna, valor e unidade. |
| Ranking | Não muda se o ranker continuar recebendo apenas texto original; usar campos do sidecar como termos ou filtros criaria outra configuração. | Pode mudar tokens, scores e ordem; precisa ser medido como nova configuração. |
| Orçamento e armazenamento | Medir bytes do sidecar. Se seus campos forem enviados como contexto, contabilizar cada caractere sob o mesmo orçamento; se usados apenas na validação posterior, declarar que não foram enviados. | Medir bytes armazenados e contar todo texto adicionado no orçamento; não conceder contexto extra. |
| Proveniência | Registrar hash do PDF, ID/offset do chunk, página, bbox, tabela, linha/coluna, cabeçalho, célula, unidade, extrator e versão; distinguir nativo, inferido e não disponível. | Além dos mesmos vínculos, marcar intervalos como transcrição original ou transformação adicionada; fornecer regra, versão e origem de cada campo. |
| Risco de associação incorreta | Chave/bbox errados podem vincular célula ao chunk errado; não pressupor que uma caixa ou página resolve semântica. | Transformação incorreta pode fabricar afirmação, confundir cabeçalhos/unidades ou transmitir texto adicionado como original. |
| Compatibilidade e complexidade | Requer esquema e vínculos verificáveis; pode manter texto do ranker histórico, mas consumidores precisam entender o sidecar. | Integração como texto é simples conceitualmente, mas exige transformação e julgamento de cada relação, mais controle de custo e contaminação do ranking. |

Se o PO autorizar um experimento, congelar corpus, extrator, regras e hashes, avaliar os mapeamentos no PDF original e comparar com o pipeline histórico sob mesmo k e orçamento. Medir separadamente preservação de relações, referências resolvíveis, suporte semântico, falhas, tamanho e custo de processamento. Não inferir título, célula, ordem em colunas ou unidade ausentes. Qualquer nova dependência estrutural, mudança de arquitetura ou API exige avaliação, decisão e ADR quando aplicável antes da implementação. A aprovação dos resultados da STORY-063 não autoriza automaticamente uma dessas opções.
