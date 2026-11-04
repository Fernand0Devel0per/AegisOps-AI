# GL-LAT — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://gitlab.com/gitlab-com/runbooks/-/blob/v2.198.1/docs/gitaly/gitaly-latency.md
- Source path: `docs/gitaly/gitaly-latency.md`
- Source revision: `v2.198.1`
- Source sections: Symptoms; 1. Check the triage dashboard to assess the impact
- Source SHA-256: `50891600cd8e813e1f470147b12738471a0ca25e696384cdc9179049c7082f87`
- License: MIT; notice: `licenses/gitlab-v2.198.1-MIT.txt`
- Attribution: GitLab.com / Runbooks e respectivos autores; preservar avisos aplicáveis.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

This scenario concerns latency in the Gitaly service. Its triage examines Gitaly p95 latency to identify affected servers. A general service request p95 does not identify Gitaly as the affected component.
