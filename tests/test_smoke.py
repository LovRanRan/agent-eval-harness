"""Smoke test: the package imports and exposes a version.

Scaffold-level guard (Commit 0.b). Real eval-API tests land with Commit 1+.
"""

from __future__ import annotations

import agent_eval_harness


def test_package_imports() -> None:
    assert agent_eval_harness is not None


def test_version_is_a_nonempty_string() -> None:
    version = agent_eval_harness.__version__
    assert isinstance(version, str)
    assert version
