# BK-MEM — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://github.com/moatazeldebsy/backstage-platform-template/blob/6b0aad93ad05119d0d464eb0eac9e829f8212d45/docs/runbooks/high-memory.md
- Source path: `docs/runbooks/high-memory.md`
- Source revision: `6b0aad93ad05119d0d464eb0eac9e829f8212d45`
- Source sections: Alert Description; 1. Identify the high-memory pods; 2. Check for a memory leak pattern
- Source SHA-256: `400b571809b930d4dbb819a3c5fd06137aff6d677f8920bbd53fb9013d9b0caa`
- License: MIT; notice: `licenses/backstage-MIT.txt`
- Attribution: backstage-platform-template contributors; preservar copyright e permissão MIT em cópias ou partes substanciais.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

For high memory usage relative to a limit, examine the scope and the available history of usage. Additional measurements are needed to investigate a sustained rise or a possible leak; two period averages do not prove a continuous trend or an impending out-of-memory event.
