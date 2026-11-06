# DU-CPU — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://github.com/durrello/incident-response-runbooks/blob/15a4a5453fb76425337ac42ea75d7d84bae62822/runbooks/high-cpu.md
- Source path: `runbooks/high-cpu.md`
- Source revision: `15a4a5453fb76425337ac42ea75d7d84bae62822`
- Source sections: 1. Confirm scope
- Source SHA-256: `87f296761e1cd2b3706fd43d615418e32e6f55e852b8a229ec865c6ed1d0bbd3`
- License: MIT; notice: `licenses/durrell-MIT.txt`
- Attribution: Durrell Gemuh e colaboradores; preservar copyright e aviso de permissão MIT em cópias ou partes substanciais.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

For high CPU usage, clarify the scope: is the observation limited to one component or spread across the service? If separately available, compare latency and error observations over the same period. High CPU alone does not establish user impact or its cause.
