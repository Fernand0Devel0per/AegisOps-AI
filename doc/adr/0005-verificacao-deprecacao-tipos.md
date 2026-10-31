# ADR-0005 — Verificação complementar de deprecações de tipos

## Status

`accepted` em 2026-10-31. O PO solicitou impedir a recorrência da anotação deprecada na STORY-012 e autorizou uma dependência de desenvolvimento caso necessária. Esta decisão complementa o [ADR-0003](0003-ambiente-python-qualidade.md), que continua vigente: mypy, Ruff e as demais validações permanecem obrigatórios. Não altera dependências de runtime nem substitui outro ADR.

## Contexto e alternativas

O typeshed incluído no mypy 2.4.1 não marca como deprecada a sobrecarga de `contextlib.asynccontextmanager` que recebe `AsyncIterator`. No Python 3.14.8, `mypy --enable-error-code deprecated` aceitou um exemplo inválido. Com uma cópia integral mais recente do typeshed e `--custom-typeshed-dir`, o mesmo mypy rejeitou o exemplo e aceitou `AsyncGenerator`; isso exigiria distribuir e manter separadamente o conjunto de stubs e sua compatibilidade.

Outra alternativa seria um verificador de sintaxe próprio, mas ele precisaria resolver aliases e definições de tipos de forma confiável. O Pyright 1.1.414 já inclui os stubs necessários e, em teste isolado com Python 3.14.8, rejeitou o exemplo com `reportDeprecated` como erro e aceitou o correto. O pacote Python do Pyright é um wrapper mantido pela comunidade e usa Node.js; o extra `nodejs` adiciona um binário travado, maior que uma solução puramente Python, mas evita obter Node em tempo de execução após a instalação.

## Decisão

Adicionar `pyright[nodejs]==1.1.414` ao grupo de desenvolvimento e travar suas transitivas em `uv.lock` (incluindo `nodejs-wheel-binaries==24.19.0` na resolução observada). Configurar Python 3.14, análise de `src/`, `tests/` e `scripts/` e `reportDeprecated = "error"`. Executar `uv run --offline --locked --no-sync pyright` localmente após setup e a versão equivalente no workflow Quality. Preservar o mypy e suas opções existentes. Testes exercitam o mesmo comando configurado em exemplos temporários inválido e válido.

## Consequências e limites

O diagnóstico depende das definições incluídas na versão fixada; atualizar Pyright pode alterar suas regras e exige executar os testes de regressão. A instalação inicial requer baixar Node e o pacote, e a disponibilidade de wheels varia entre plataformas. Arquivos fora dos diretórios analisados e exclusões explícitas não são cobertos. A análise detecta usos de APIs marcadas como deprecadas no typeshed, não prova conformidade semântica de todos os programas. `yaml` em `scripts/validate_repository.py` pode produzir aviso de resolução, pois PyYAML é instalado separadamente para validação documental.

Ruff UP043 sugere omitir o `None` padrão de `AsyncGenerator` em Python 3.14. Para atender à forma explícita solicitada pelo PO, `lifespan` tem uma exceção pontual dessa regra de estilo; a verificação de deprecação do Pyright não é suprimida.

## Evidências e referências

- [HANDOFF-012](../../agents/handoffs/HANDOFF-012.yaml): comandos, versões, resultados e limites.
- [Typeshed: contextlib](https://github.com/python/typeshed/blob/main/stdlib/contextlib.pyi): sobrecargas e deprecação.
- [Configuração do Pyright](https://github.com/microsoft/pyright/blob/main/docs/configuration.md): `reportDeprecated` e tipos de diagnósticos.
- [Pyright para Python](https://pypi.org/project/pyright/1.1.414/): wrapper, extra Node e formas de instalação.
- [Ruff UP043](https://docs.astral.sh/ruff/rules/unnecessary-default-type-args/): argumentos de tipo padrão.
