"""Busca lexical determinística sobre os trechos locais do corpus C1."""

import hashlib
import unicodedata
from dataclasses import dataclass
from importlib.resources import files
from typing import Literal

CORPUS_VERSION = "C1-2026-11-04.1"
CORPUS_SHA256 = "562b1a8bf10a96ce8f83d41dd43ad102256e5c006bc44c67d78b3a31f691c3cb"
# Os dados fixados são cópia dos campos do manifesto revisado; não são termos de busca.
_UNITS = (
    (
        "GL-DIAG",
        "datasets/runbooks/gl-diag.md",
        "fcb659d0c461e2d80394586507eb21298e3891784872a1f5bf84fb0a7870b934",
        "https://gitlab.com/gitlab-com/runbooks/-/blob/v4.111.0/docs/tutorials/diagnosis.md",
        "v4.111.0",
        "0ea7ce983ff5bf6c9bb7d9675dfa01ccfd69fb537592bce33045178157469df1",
    ),
    (
        "GL-GITALY",
        "datasets/runbooks/gl-gitaly.md",
        "3d2869b190a3e95fefccf2f279dc5b29051f2477453222038911e04e68415634",
        "https://gitlab.com/gitlab-com/runbooks/-/blob/v2.180.0/docs/gitaly/git-high-cpu-and-memory-usage.md",
        "v2.180.0",
        "8ed0222854a307de2ef9062577ee8e046869cf541f968ecaa5c20946e5f67de0",
    ),
    (
        "GL-LAT",
        "datasets/runbooks/gl-lat.md",
        "2774c3a6dcb359aec7611783bfbc3ed5a733d873d927f25568cf8b1cb5cb53bb",
        "https://gitlab.com/gitlab-com/runbooks/-/blob/v2.198.1/docs/gitaly/gitaly-latency.md",
        "v2.198.1",
        "50891600cd8e813e1f470147b12738471a0ca25e696384cdc9179049c7082f87",
    ),
    (
        "PO-CPU",
        "datasets/runbooks/po-cpu.md",
        "0d0e8e8e71288a7461ad7212d275b06f4c4313d71cc5dda69098809d779aa21e",
        "https://github.com/prometheus-operator/runbooks/blob/a685d14cf5128bb30e2bf935c3983decd772d885/content/runbooks/kubernetes/CPUThrottlingHigh.md",
        "a685d14cf5128bb30e2bf935c3983decd772d885",
        "cdfb846e71a3c5edb19d73a56b1137158d1ee2b406a9db174f6605e1ffd4c30b",
    ),
    (
        "PO-MEM",
        "datasets/runbooks/po-mem.md",
        "afe26e5487794fbeff902c911d72bf704a758c0eeb462447375ac80538aaed6b",
        "https://github.com/prometheus-operator/runbooks/blob/a685d14cf5128bb30e2bf935c3983decd772d885/content/runbooks/kubernetes/KubeMemoryOvercommit.md",
        "a685d14cf5128bb30e2bf935c3983decd772d885",
        "d441f56b3548f015ebd9e2ad4483cd714322e67f25aee58a036159d8a6bc2ed1",
    ),
    (
        "PO-KCLIENT",
        "datasets/runbooks/po-kclient.md",
        "4d4eafadc005322e461708edbf9092a5d3d28b5a275e3303308584a4019edc86",
        "https://github.com/prometheus-operator/runbooks/blob/a685d14cf5128bb30e2bf935c3983decd772d885/content/runbooks/kubernetes/KubeClientErrors.md",
        "a685d14cf5128bb30e2bf935c3983decd772d885",
        "5202eafd0a0a0d0f6fec3f587c652d20bafb334223b80bd127568031a95a9293",
    ),
    (
        "DU-CPU",
        "datasets/runbooks/du-cpu.md",
        "91231b1f9b79b4e28619c0261a73ef5bc028d18b644c1207d78e85df9b3db68b",
        "https://github.com/durrello/incident-response-runbooks/blob/15a4a5453fb76425337ac42ea75d7d84bae62822/runbooks/high-cpu.md",
        "15a4a5453fb76425337ac42ea75d7d84bae62822",
        "87f296761e1cd2b3706fd43d615418e32e6f55e852b8a229ec865c6ed1d0bbd3",
    ),
    (
        "DU-5XX",
        "datasets/runbooks/du-5xx.md",
        "de5cc367e13397e983c8ce084b08fcac6d1283eec1a26c841fd527b5a74470bf",
        "https://github.com/durrello/incident-response-runbooks/blob/15a4a5453fb76425337ac42ea75d7d84bae62822/runbooks/high-error-rate.md",
        "15a4a5453fb76425337ac42ea75d7d84bae62822",
        "c320e3a628956ea3d4f0aa2a474d46a42e185b01517cda586f5a12cd99816026",
    ),
    (
        "BK-CPU",
        "datasets/runbooks/bk-cpu.md",
        "f2f4e71939d31252ea425e443228d7a0db710fd5ce966a99ab1d68ac208ebd8a",
        "https://github.com/moatazeldebsy/backstage-platform-template/blob/6b0aad93ad05119d0d464eb0eac9e829f8212d45/docs/runbooks/high-cpu.md",
        "6b0aad93ad05119d0d464eb0eac9e829f8212d45",
        "29bf091a4217e323ecfb6e19f230a211aaf4954a8f852a98ed74ae7b6b308f5d",
    ),
    (
        "BK-MEM",
        "datasets/runbooks/bk-mem.md",
        "e91a2a0a709c5f5c0811c6ef724cd563f23a18935182844870d29173eae5bbc1",
        "https://github.com/moatazeldebsy/backstage-platform-template/blob/6b0aad93ad05119d0d464eb0eac9e829f8212d45/docs/runbooks/high-memory.md",
        "6b0aad93ad05119d0d464eb0eac9e829f8212d45",
        "400b571809b930d4dbb819a3c5fd06137aff6d677f8920bbd53fb9013d9b0caa",
    ),
    (
        "URL-LAT",
        "datasets/runbooks/url-lat.md",
        "e69da6b2d2c5d4dd232ecc3c72f465aeba71c5ec2a538cb2d2630194affb7c95",
        "https://github.com/RETR0-OS/MLH_PE_URL_Shortener/blob/c47e12d39277b379ef43703b2f71b8863c888a9d/docs/Incident%20Response/runbooks/INCIDENT-PLAYBOOK.md",
        "c47e12d39277b379ef43703b2f71b8863c888a9d",
        "9fea1f5e6161d2cf58fa33b9347217239b7096bc2b6084230692b442cda6484e",
    ),
)


class InvalidQuery(ValueError):
    """Consulta ou limite inválido."""


class CorpusError(RuntimeError):
    """Recurso ou proveniência indisponível ou inválida."""


@dataclass(frozen=True)
class Passage:
    id: str
    path: str
    corpus_version: str
    sha256: str
    source_url: str
    source_version: str
    text: str
    score: int


@dataclass(frozen=True)
class RetrievalResult:
    state: Literal["returned", "abstained"]
    passages: tuple[Passage, ...]


def _tokens(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(
        c for c in normalized if not unicodedata.category(c).startswith("M")
    )
    stripped = stripped.casefold()
    words: list[str] = []
    current = ""
    for char in stripped:
        if char.isalnum():
            current += char
        elif current:
            words.append(current)
            current = ""
    if current:
        words.append(current)
    return set(words)


def _read_resource(name: str) -> bytes:
    return files("aegisops").joinpath("data", "runbooks", name).read_bytes()


def _load_passages() -> tuple[Passage, ...]:
    passages = []
    canonical = []
    try:
        for identifier, path, digest, source, version, source_digest in _UNITS:
            data = _read_resource(path.rsplit("/", 1)[-1])
            if hashlib.sha256(data).hexdigest() != digest:
                raise CorpusError("Hash da unidade divergente")
            text = data.decode("utf-8")
            required = (
                f"# {identifier} —",
                f"- Corpus version: {CORPUS_VERSION}",
                f"- Source: {source}",
                f"- Source revision: `{version}`",
                f"- Source SHA-256: `{source_digest}`",
            )
            if (
                not all(item in text for item in required)
                or text.count("## Excerpt\n") != 1
            ):
                raise CorpusError("Proveniência ou trecho inválido")
            excerpt = text.split("## Excerpt\n", 1)[1].strip()
            if not excerpt:
                raise CorpusError("Trecho vazio")
            canonical.append((path, digest))
            passages.append(
                Passage(
                    identifier,
                    path,
                    CORPUS_VERSION,
                    digest,
                    source,
                    version,
                    excerpt,
                    0,
                )
            )
    except (OSError, UnicodeError) as exc:
        raise CorpusError("Corpus indisponível ou ilegível") from exc
    if len({p.id for p in passages}) != len(passages) or len(
        {p.path for p in passages}
    ) != len(passages):
        raise CorpusError("Unidade duplicada")
    digest_lines = "".join(f"{digest}  {path}\n" for path, digest in sorted(canonical))
    if hashlib.sha256(digest_lines.encode()).hexdigest() != CORPUS_SHA256:
        raise CorpusError("Hash do corpus divergente")
    return tuple(passages)


def retrieve(query: str, k: int = 5) -> RetrievalResult:
    """Retorna até k trechos; abstenção não demonstra ausência semântica."""
    if not isinstance(query, str) or len(query) > 4096 or not _tokens(query):
        raise InvalidQuery("Consulta inválida")
    if type(k) is not int or not 1 <= k <= 5:
        raise InvalidQuery("k deve ser inteiro entre 1 e 5")
    terms = _tokens(query)
    matches = []
    for passage in _load_passages():
        score = len(terms & _tokens(passage.text))
        if score:
            matches.append(
                Passage(
                    passage.id,
                    passage.path,
                    passage.corpus_version,
                    passage.sha256,
                    passage.source_url,
                    passage.source_version,
                    passage.text,
                    score,
                )
            )
    matches.sort(key=lambda p: (-p.score, p.id))
    selected = tuple(matches[:k])
    return RetrievalResult("returned" if selected else "abstained", selected)
