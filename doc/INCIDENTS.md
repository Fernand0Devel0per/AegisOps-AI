# Incidentes sintéticos para descoberta

## Estado e finalidade

Entrega da [STORY-002](../roadmap/stories/STORY-002.yaml), aprovada pelo PO em 2026-10-30; a descoberta completa ainda depende do gate da STORY-004. Os três incidentes, serviços, origens, timestamps, valores e classificações foram criados como dados fictícios; não são medições, garantias operacionais ou regras de produção. Os sinais descrevem os serviços fictícios, não a telemetria da plataforma AegisOps AI. Os nomes de severidade `media` e `alta` são rótulos esperados apenas para estes exemplos; seu significado e suas regras ainda não foram aprovados.

| Cenário | Fixture | Resultado esperado proposto | Leitura rastreável |
|---|---|---|---|
| Latência elevada | [INC-001](../datasets/incidents/inc-001-latencia.json) | `media` | p95 aumenta de 120 para 900 ms (EVD-001-01 e EVD-001-02); 0,5% de 5xx no segundo período (EVD-001-03). |
| Taxa HTTP 5xx alta | [INC-002](../datasets/incidents/inc-002-erros-5xx.json) | `alta` | 5xx aumenta de 1% para 20% (EVD-002-01 e EVD-002-02); CPU média de 92% no segundo período (EVD-002-03). |
| Saturação de recursos | [INC-003](../datasets/incidents/inc-003-saturacao.json) | `alta` | Memória média aumenta de 60% para 97% (EVD-003-01 e EVD-003-02); CPU média de 95% no segundo período (EVD-003-03). |

A coexistência de sinais não prova relação causal. Em INC-003, saturação é o nome proposto do cenário de alta utilização; os dados não comprovam exaustão ou impacto. Cada fixture explicita o que é observável e o que não pode ser concluído.

## Como ler e reproduzir

Na raiz do repositório, com Python 3, sem rede e sem credenciais:

```sh
python3 -m json.tool datasets/incidents/inc-001-latencia.json
python3 -m json.tool datasets/incidents/inc-002-erros-5xx.json
python3 -m json.tool datasets/incidents/inc-003-saturacao.json
python3 scripts/validate_incidents.py
```

As entradas e resultados esperados estão integralmente nos arquivos. Cada janela UTC usa início inclusivo e fim exclusivo; os períodos de sinal são agregações nos cinco minutos indicados. O p95 é um percentil de duração das requisições do período, não uma média dos percentis; `ms` é milissegundo. Percentuais de CPU e memória referem-se, respectivamente, à capacidade alocada de CPU e ao limite de memória do serviço. Para 5xx, os campos `numerator` e `denominator` são contagens fictícias de respostas 5xx e de todas as respostas HTTP; `value` é 100 vezes o quociente. As contagens são específicas de cada período.

Em cada arquivo, `signals` registra os valores; `evidence` relaciona cada ID de evidência a um `signal_id` do mesmo arquivo; `expected.evidence_ids` e as justificativas citam esses IDs. Resolva a citação na lista de evidências e depois o sinal pelo ID. O resumo de evidência auxilia a leitura, mas o sinal é a fonte do valor. O verificador testa estrutura, unicidade global, unidades, valores, janelas, aritmética de 5xx e referências. Ele não verifica se a justificativa decorre semanticamente dos sinais, se uma severidade está correta ou se uma regra existe; essa comparação exige leitura e revisão. O formato é apenas o necessário para estes exemplos e não constitui contrato final da aplicação.

## Ambiguidades para STORY-003

[Q-002](decisions/open-questions.md) permanece aberta. As classificações propostas não definem a partir de qual valor há degradação nem como comparar `media` e `alta`. A próxima história deverá examinar, com o PO, quais indicadores e períodos sustentam cada severidade, limites e inclusão ou exclusão de suas fronteiras, duração e amostragem, agregação e mudança em relação a uma referência, além de como sinais simultâneos, conflitos e dados ausentes afetam o resultado. Os exemplos não fornecem limites aprovados nem cobrem exaustivamente os casos de fronteira. INC-001 apresenta 0,5% de 5xx sem concluir que seja aceitável: falta uma política.

Segundo o [ADR-0002](adr/0002-llm-local-primeira-vertical.md), a futura triagem usa regras para determinar severidade e verificar referências; o LLM local explica o resultado, e falha ou rejeição da explicação preserva a saída básica com limitação sinalizada. Nada disso é executado ou integrado por estas fixtures. Uma referência existente não prova, por si, que a afirmação é sustentada.
