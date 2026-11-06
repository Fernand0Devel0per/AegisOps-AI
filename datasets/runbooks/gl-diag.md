# GL-DIAG — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://gitlab.com/gitlab-com/runbooks/-/blob/v4.111.0/docs/tutorials/diagnosis.md
- Source path: `docs/tutorials/diagnosis.md`
- Source revision: `v4.111.0`
- Source sections: Symptom- vs cause-based alerting; Querying: filtering and grouping; Aggregation
- Source SHA-256: `0ea7ce983ff5bf6c9bb7d9675dfa01ccfd69fb537592bce33045178157469df1`
- License: MIT; notice: `licenses/gitlab-v4.111.0-MIT.txt`
- Attribution: GitLab.com / Runbooks e respectivos autores; preservar avisos de copyright e licença aplicáveis.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

For latency or error symptoms, first identify the affected service and examine how affected requests differ from the overall request population. If suitable request data exists, filter and group it by available dimensions and compare distributions. Aggregated or sampled views can hide detail; obtain additional evidence before selecting a hypothesis.
