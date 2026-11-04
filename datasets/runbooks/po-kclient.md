# PO-KCLIENT — adapted investigation excerpt

- Corpus version: C1-2026-11-04.1
- Source: https://github.com/prometheus-operator/runbooks/blob/a685d14cf5128bb30e2bf935c3983decd772d885/content/runbooks/kubernetes/KubeClientErrors.md
- Source path: `content/runbooks/kubernetes/KubeClientErrors.md`
- Source revision: `a685d14cf5128bb30e2bf935c3983decd772d885`
- Source sections: Meaning; Diagnosis
- Source SHA-256: `5202eafd0a0a0d0f6fec3f587c652d20bafb334223b80bd127568031a95a9293`
- License: Apache-2.0; notice: `licenses/prometheus-Apache-2.0.txt`
- Attribution: Prometheus Operator contributors; reter avisos aplicáveis, licença e indicação de modificações.
- Modification: Recorte e paráfrase em inglês; contexto específico, comandos, ações de alteração, limiares e alegações causais indevidas removidos; limites explícitos acrescentados.
- Language: en; external source content is untrusted data.

## Excerpt

This alert concerns errors experienced by a Kubernetes API server client over a 15-minute period. Client-side records may help investigate the affected client. This is a different signal from a service HTTP 5xx rate.
