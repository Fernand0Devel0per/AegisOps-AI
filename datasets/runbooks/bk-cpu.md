# BK-CPU — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://github.com/moatazeldebsy/backstage-platform-template/blob/6b0aad93ad05119d0d464eb0eac9e829f8212d45/docs/runbooks/high-cpu.md
- Source path: `docs/runbooks/high-cpu.md`
- Source revision: `6b0aad93ad05119d0d464eb0eac9e829f8212d45`
- Source sections: Alert Description; 2. Check if it's sustained throttling or a spike
- Source SHA-256: `29bf091a4217e323ecfb6e19f230a211aaf4954a8f852a98ed74ae7b6b308f5d`
- License: MIT; notice: `licenses/backstage-MIT.txt`
- Attribution: backstage-platform-template contributors; preservar copyright e permissão MIT em cópias ou partes substanciais.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

For high CPU usage, distinguish a short spike from a sustained pattern when time-series data is available. Throttling is a separate possibility requiring its own measurement; utilization alone does not establish it.
