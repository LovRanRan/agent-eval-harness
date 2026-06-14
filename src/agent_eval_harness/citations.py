"""Citation extraction + repo-backed symbol resolution for citation_grounding.

`extract_cited_symbols` pulls candidate code references out of an agent's
free-form answer (dotted paths, backticked identifiers, file paths). A
`RepoSymbolResolver` then checks whether each reference actually exists in the
repo clone — so hallucinated citations are caught and lower the grounding score.
"""

from __future__ import annotations

import re
from pathlib import Path

from agent_eval_harness.datasets import Task

# `backticked` spans, dotted.paths (a.b.c), and path/like/file.py references.
_BACKTICK = re.compile(r"`([^`]+)`")
_DOTTED = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)\b")
_PATH = re.compile(r"\b([A-Za-z0-9_./-]+\.(?:py|js|ts|go|rs|java))\b")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_STOP = frozenset({"e.g", "i.e", "etc", "vs", "self.", "os.path"})
_MAX_SYMBOLS = 25


def extract_cited_symbols(text: str) -> list[str]:
    """Extract de-duplicated candidate code symbols / paths cited in `text`."""
    found: list[str] = []
    seen: set[str] = set()

    def _add(candidate: str) -> None:
        candidate = candidate.strip().strip("`'\"().,:;").strip()
        if not candidate or candidate.lower() in _STOP or candidate in seen:
            return
        # keep only things that look like code references, not prose
        if (
            _DOTTED.fullmatch(candidate)
            or _PATH.fullmatch(candidate)
            or ("_" in candidate and _IDENT.match(candidate))
        ):
            seen.add(candidate)
            found.append(candidate)

    for match in _BACKTICK.findall(text):
        for token in re.split(r"[\s,(]", match):
            _add(token)
    for match in _PATH.findall(text):
        _add(match)
    for match in _DOTTED.findall(text):
        _add(match)
    return found[:_MAX_SYMBOLS]


def default_repo_slug(repo_url: str) -> str:
    """Match the on-disk clone naming used by the live invokers."""
    return re.sub(r"[^A-Za-z0-9]+", "_", repo_url.removeprefix("https://").removesuffix(".git"))


class RepoSymbolResolver:
    """Task-aware resolver: does a cited symbol exist in the task's repo clone?

    Resolution order: a matching file path exists, OR the symbol's final
    component is defined (`def`/`class`) anywhere in the repo. Missing clones
    resolve to False (conservative — counts as ungrounded).
    """

    def __init__(self, clone_roots: list[Path], *, slug: object = default_repo_slug) -> None:
        self._clone_roots = clone_roots
        self._slug = slug

    def _repo_dir(self, task: Task) -> Path | None:
        slug_fn = self._slug
        assert callable(slug_fn)
        slug = str(slug_fn(task.repo_url))
        for root in self._clone_roots:
            candidate = root / slug
            if candidate.is_dir():
                return candidate
        return None

    def __call__(self, task: Task, symbol: str) -> bool:
        repo_dir = self._repo_dir(task)
        if repo_dir is None:
            return False
        # file path reference
        if _PATH.fullmatch(symbol):
            tail = symbol.split("/", 1)[-1] if "/" in symbol else symbol
            return (repo_dir / symbol).exists() or any(repo_dir.rglob(Path(tail).name))
        # dotted path or identifier -> check the final component is defined
        name = symbol.split(".")[-1]
        if not _IDENT.match(name):
            return False
        pattern = re.compile(rf"^\s*(?:async\s+def|def|class)\s+{re.escape(name)}\b", re.MULTILINE)
        for path in list(repo_dir.rglob("*.py"))[:2000]:
            try:
                if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                    return True
            except OSError:
                continue
        return False
