# Demonstração local da primeira vertical

A API recebe um incidente sintético, aplica o contrato e os limiares determinísticos da STORY-020 e pede ao Qwen local uma seleção de frases canônicas. Um verificador independente confere os IDs e os vínculos com os sinais antes de montar o texto. Não há causa raiz confirmada nem remediação. Os limiares são sintéticos e referências não comprovam a verdade dos dados. Evidências e limitações dos testes estão em [avaliação](decisions/story-021-avaliacao.md) e [handoff](../agents/handoffs/HANDOFF-021.yaml).

## Preparação

São necessários Python e uv conforme [desenvolvimento local](DEVELOPMENT.md), além de Git, compilador C/OpenMP, `make`, systemd de usuário e o cliente `hf` do Hugging Face. A primeira obtenção do código, dependências e pesos requer internet; as chamadas da investigação usam somente loopback. Há uma alternativa sem modelo via fallback, mas não se deve confundi-la com a explicação por inferência real. O modelo convertido ocupa aproximadamente 19,4 GB em disco; os testes locais do Qwen tiveram pico RSS de cerca de 6,25 GiB por processo. Antes da execução, confira memória disponível e capacidade do disco para o seu ambiente.

Instale o projeto e prepare Colibri e pesos uma vez, fora do repositório. Os diretórios abaixo são exemplos; substitua-os por caminhos locais se necessário. O comando de download fixa a revisão avaliada; o cliente `hf` é ferramenta externa de preparação, não dependência travada da aplicação. O exemplo usa `HF_HUB_DISABLE_XET=1` para permitir download retomável por HTTPS, conforme o experimento local.

```sh
uv sync --locked --no-editable
git clone https://github.com/JustVugg/colibri.git "$HOME/.local/share/aegisops-colibri-demo"
git -C "$HOME/.local/share/aegisops-colibri-demo" checkout e0db083cdc9e563e0766cc6fc661ef23c32298e0
make -C "$HOME/.local/share/aegisops-colibri-demo/c" qwen36
HF_HUB_DISABLE_XET=1 hf download Justvugg/Qwen3-Coder-30B-A3B-colibri-int4 \
  --revision d839110a17d31b4e6fa9f3d973b751f779b6b9c6 \
  --local-dir "$HOME/.local/share/aegisops-models/qwen3-coder-30b-a3b-int4"
```

O checkpoint convertido informa licença Apache-2.0; consulte o [modelo](https://huggingface.co/Justvugg/Qwen3-Coder-30B-A3B-colibri-int4) e as condições de suas dependências. A disponibilidade de pacotes, compilação e hardware varia por ambiente; os comandos são instruções de reprodução, não prova de que todo clone foi testado. Após alterações em `src`, reinstale o pacote não editável:

```sh
uv sync --offline --locked --no-editable --reinstall-package aegisops-ai
```

## Iniciar localmente

Em um terminal, inicie o Colibri com fila zero. O teto de 512 é para tokens de saída; não é tamanho de contexto. Limites de processo são os testados no Linux local, não garantias universais:

```sh
systemd-run --user --scope --quiet -p MemoryMax=9G -p MemorySwapMax=1G -p CPUQuota=400% \
  "$HOME/.local/share/aegisops-colibri-demo/c/coli" serve \
  --model "$HOME/.local/share/aegisops-models/qwen3-coder-30b-a3b-int4" \
  --host 127.0.0.1 --port 18999 --cap 32 --ctx 2048 --ngen 512 \
  --gpu none --temp 0 --max-queue 0
```

Em outro terminal, após o Colibri ficar pronto, inicie a API em loopback:

```sh
uv run --offline --locked --no-sync uvicorn aegisops.api:app --host 127.0.0.1 --port 18765 --no-access-log
```

A API usa `127.0.0.1:18999` para o Colibri. Para outra porta local, defina `AEGISOPS_COLIBRI_PORT` antes de iniciar a API; não é aceita URL remota. `/health` da API não exige que o modelo esteja disponível.

## Enviar e conferir

Em um terceiro terminal, a partir da raiz:

```sh
curl --fail-with-body --max-time 320 -sS -H 'Content-Type: application/json' \
  --data-binary @datasets/incidents/inc-001-latencia.json \
  http://127.0.0.1:18765/v1/investigations | python3 -m json.tool
```

Para a fixture INC-001, confira `triage.state=classificado`, `triage.severity=media` e as três observações e evidências `EVD-001-01`, `EVD-001-02` e `EVD-001-03`. Com inferência válida, `explanation.state=verificada`; `text` é composto exclusivamente das frases de `sentences`, que trazem seus IDs de sinal e evidência. O modelo pode escolher uma parte das frases, mas deve incluir a de severidade máxima. Uma classificação parcial e suas métricas ausentes permanecem em `triage.limitations`. O campo `triage.explanation_state=nao_solicitada` pertence ao resultado básico imutável da STORY-020; o estado efetivo desta etapa fica em `explanation.state`.

Se o Colibri estiver indisponível, ocupado ou exceder 300 s, o mesmo envio preserva `triage` e retorna `explanation.state=indisponivel`, sem texto e com limitação. Resposta rejeitada retorna `rejeitada`, também sem texto. Um timeout encerra a espera e conexão do cliente, mas **não garante que o servidor tenha cancelado a inferência**. A fila zero evita acumular novos pedidos enquanto o modelo estiver ocupado; o operador pode encerrá-lo no terminal. Quando terminar, interrompa ambos os processos nos respectivos terminais.

Entrada JSON malformada gera `400`, corpo acima de 256 KiB gera `413` e incidente que viola o contrato gera `422` com caminhos e códigos, sem refletir valores recebidos. Uma entrada válida sem sinais nem evidências retorna `insuficiente` e não solicita explicação. Um incidente classificável com mais de 16 observações ou prompt acima de 4096 bytes preserva triagem e informa explicação indisponível. Esta operação responde na mesma requisição, sem persistência ou consulta posterior da investigação.
