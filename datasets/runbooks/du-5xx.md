# DU-5XX — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://github.com/durrello/incident-response-runbooks/blob/15a4a5453fb76425337ac42ea75d7d84bae62822/runbooks/high-error-rate.md
- Source path: `runbooks/high-error-rate.md`
- Source revision: `15a4a5453fb76425337ac42ea75d7d84bae62822`
- Source sections: 1. Triage (first 5 minutes)
- Source SHA-256: `c320e3a628956ea3d4f0aa2a474d46a42e185b01517cda586f5a12cd99816026`
- License: MIT; notice: `licenses/durrell-MIT.txt`
- Attribution: Durrell Gemuh e colaboradores; preservar copyright e aviso de permissão MIT em cópias ou partes substanciais.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

For elevated HTTP 5xx responses, examine the scope of errors across endpoints or regions if those observations are available. Consider recent changes as possibilities to investigate, without assuming that a change happened or caused the errors.
