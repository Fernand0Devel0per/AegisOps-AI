# PO-CPU — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://github.com/prometheus-operator/runbooks/blob/a685d14cf5128bb30e2bf935c3983decd772d885/content/runbooks/kubernetes/CPUThrottlingHigh.md
- Source path: `content/runbooks/kubernetes/CPUThrottlingHigh.md`
- Source revision: `a685d14cf5128bb30e2bf935c3983decd772d885`
- Source sections: Meaning; Diagnosis
- Source SHA-256: `cdfb846e71a3c5edb19d73a56b1137158d1ee2b406a9db174f6605e1ffd4c30b`
- License: Apache-2.0; notice: `licenses/prometheus-Apache-2.0.txt`
- Attribution: Prometheus Operator contributors; reter avisos aplicáveis, licença e indicação de modificações.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

The alert concerns elevated CPU throttling of processes. Diagnosis considers application behaviour and the relationship between CPU requests and usage. CPU utilization alone is not evidence that throttling has occurred.
