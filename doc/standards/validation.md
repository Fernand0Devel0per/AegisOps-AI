# Validação dos artefatos documentais

Na raiz, executar com Python 3 e PyYAML disponível:

```bash
python3 scripts/validate_repository.py
git diff --check
git diff --cached --check
```

O ambiente usado no bootstrap já tinha PyYAML 6.0.2. Para um ambiente que não o tenha, uma opção isolada é:

```bash
python3 -m venv /tmp/aegisops-doc-validation
/tmp/aegisops-doc-validation/bin/python -m pip install 'PyYAML==6.0.2'
/tmp/aegisops-doc-validation/bin/python scripts/validate_repository.py
```

Esses comandos de instalação são instruções de reprodução, não evidência de instalação realizada. PyYAML é ferramenta de documentação e não integra o ambiente de produto; o setup e o lockfile estão descritos em [desenvolvimento local](../DEVELOPMENT.md).

Exceto pela referência histórica ao plano local descrita abaixo, o validador rejeita YAML malformado/chaves duplicadas, campos obrigatórios ausentes, tipos estruturais básicos incorretos, IDs repetidos, estados/prioridades inválidos, inconsistência índice/arquivos, vínculos inexistentes, dependências cíclicas, histórias prontas sem contrato, ACs sem mapeamento em specs, links locais Markdown quebrados e referências locais de entrada inexistentes. Verifica também que artefatos `done/completed` têm handoff e evidência registrados.

`--self-test` verifica falhas representativas (chave duplicada, ciclo, índice divergente, AC sem mapeamento e caminhos inválidos), inclusive a exceção restrita para o plano local, sem modificar documentos do repositório. Usar quando o próprio validador mudar:

```bash
python3 scripts/validate_repository.py --self-test
```

No bootstrap, verificamos o hash SHA-256 do plano para comprovar sua preservação naquele momento. Valor histórico de referência:

```text
9a22c8fff517e28556e7b32cb1bd35ffe5b7306f48ad90f1f74644d22c5cc078
```

O registro da execução está em [bootstrap-validation.md](bootstrap-validation.md); os vínculos de continuidade estão em [HANDOFF-000](../../agents/handoffs/HANDOFF-000.yaml).

O validador atual ignora Markdown dentro de `.git`, `.venv` e `.local` e não lê nem verifica a existência ou o hash do arquivo local `AegisOps_AI_Plano_do_Zero.md`. Referências históricas a esse caminho exato na raiz, inclusive links Markdown, são aceitas mesmo quando o arquivo não está presente; os demais caminhos continuam sujeitos à validação. Os links para o plano podem permanecer indisponíveis em clones, como registrado em Q-014. A checagem de whitespace não inclui arquivos ignorados pelo Git.

O validador não prova semântica do produto, aprovação humana, execução de comandos citados em YAML ou funcionamento de aplicação. Não acessa links externos. Entregáveis futuros em `deliverables`/`expected_outputs` não precisam existir; referências de entrada, arquivos catalogados, links e evidências de trabalhos concluídos precisam existir, exceto a referência histórica ao plano local. A revisão manual deve comparar o conteúdo com o plano quando ele estiver disponível; sem ele, usar as fontes versionadas e registrar qualquer lacuna material. Em ambos os casos, verificar que não há requisitos inventados e confirmar o escopo de cada atividade.

A STORY-010 introduz um teste de instalação e um workflow de qualidade; instruções estão em [desenvolvimento local](../DEVELOPMENT.md). Esse teste não valida ainda funcionalidades de produto. Execução remota de CI depende de publicação autorizada e deve ser registrada apenas quando observada.
