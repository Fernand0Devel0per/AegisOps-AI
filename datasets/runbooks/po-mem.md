# PO-MEM — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://github.com/prometheus-operator/runbooks/blob/a685d14cf5128bb30e2bf935c3983decd772d885/content/runbooks/kubernetes/KubeMemoryOvercommit.md
- Source path: `content/runbooks/kubernetes/KubeMemoryOvercommit.md`
- Source revision: `a685d14cf5128bb30e2bf935c3983decd772d885`
- Source sections: Meaning; Diagnosis
- Source SHA-256: `d441f56b3548f015ebd9e2ad4483cd714322e67f25aee58a036159d8a6bc2ed1`
- License: Apache-2.0; notice: `licenses/prometheus-Apache-2.0.txt`
- Attribution: Prometheus Operator contributors; reter avisos aplicáveis, licença e indicação de modificações.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

The alert concerns Kubernetes cluster memory requests and the capacity remaining after node failure. It addresses aggregate pod requests and cluster capacity, not a service memory utilization percentage relative to its limit.
