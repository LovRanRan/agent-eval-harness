"""Tests for citation extraction + repo-backed symbol resolution."""

from __future__ import annotations

from pathlib import Path

from agent_eval_harness import (
    RepoSymbolResolver,
    Task,
    default_repo_slug,
    extract_cited_symbols,
)


def test_extract_pulls_dotted_paths_backticks_and_files() -> None:
    text = (
        "The entry point is `dispatch_request` in src/flask/app.py; it calls "
        "flask.app.Flask.full_dispatch_request. Just prose words here."
    )
    symbols = extract_cited_symbols(text)
    assert "dispatch_request" in symbols
    assert "src/flask/app.py" in symbols
    assert "flask.app.Flask.full_dispatch_request" in symbols
    assert "prose" not in symbols


def test_extract_dedupes_and_caps() -> None:
    text = "`foo_bar` `foo_bar` a.b.c a.b.c"
    symbols = extract_cited_symbols(text)
    assert symbols.count("foo_bar") == 1
    assert symbols.count("a.b.c") == 1


def _task(repo_url: str) -> Task:
    return Task(
        id="t",
        bucket="function_tracing",
        repo_url=repo_url,
        repo_pin="p",
        query="q",
        expected_key_facts=["a", "b", "c"],
        expected_route="behavioral",
    )


def test_repo_symbol_resolver_finds_defs_and_files(tmp_path: Path) -> None:
    repo_url = "https://github.com/acme/widget"
    repo_dir = tmp_path / default_repo_slug(repo_url)
    (repo_dir / "pkg").mkdir(parents=True)
    (repo_dir / "pkg" / "core.py").write_text(
        "def real_function():\n    return 1\nclass RealClass:\n    pass\n", encoding="utf-8"
    )
    resolver = RepoSymbolResolver([tmp_path])
    task = _task(repo_url)
    assert resolver(task, "real_function") is True
    assert resolver(task, "pkg.core.RealClass") is True  # final component resolves
    assert resolver(task, "pkg/core.py") is True  # file path exists
    assert resolver(task, "ghost_function") is False  # hallucinated -> ungrounded


def test_repo_symbol_resolver_grounds_real_attribute_references(tmp_path: Path) -> None:
    repo_url = "https://github.com/acme/widget"
    repo_dir = tmp_path / default_repo_slug(repo_url)
    (repo_dir / "pkg").mkdir(parents=True)
    (repo_dir / "pkg" / "core.py").write_text(
        "class Command:\n"
        "    def __init__(self, callback):\n"
        "        self.callback = callback\n"
        "    def invoke(self, ctx):\n"
        "        return ctx.invoke(self.callback, **ctx.params)\n",
        encoding="utf-8",
    )
    resolver = RepoSymbolResolver([tmp_path])
    task = _task(repo_url)
    # attribute references that actually occur in the code are grounded
    assert resolver(task, "self.callback") is True
    assert resolver(task, "ctx.params") is True
    assert resolver(task, "Command.invoke") is True  # def invoke
    # an invented attribute never appears as `.<name>` -> still ungrounded
    assert resolver(task, "self.frobnicate") is False


def test_repo_symbol_resolver_false_when_clone_missing(tmp_path: Path) -> None:
    resolver = RepoSymbolResolver([tmp_path])
    assert resolver(_task("https://github.com/none/here"), "anything") is False
