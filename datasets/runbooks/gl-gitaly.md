# GL-GITALY — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://gitlab.com/gitlab-com/runbooks/-/blob/v2.180.0/docs/gitaly/git-high-cpu-and-memory-usage.md
- Source path: `docs/gitaly/git-high-cpu-and-memory-usage.md`
- Source revision: `v2.180.0`
- Source sections: Problem: git processes spawned by Gitaly may consume significant CPU and memory; Symptoms
- Source SHA-256: `8ed0222854a307de2ef9062577ee8e046869cf541f968ecaa5c20946e5f67de0`
- License: MIT; notice: `licenses/gitlab-v2.180.0-MIT.txt`
- Attribution: GitLab.com / Runbooks e respectivos autores; preservar avisos aplicáveis.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

This scenario concerns Git processes spawned by Gitaly. One Gitaly node may show elevated CPU and anonymous memory together with many resource-intensive Git processes. A service-level CPU or memory measurement alone does not establish that this specific scenario applies.
