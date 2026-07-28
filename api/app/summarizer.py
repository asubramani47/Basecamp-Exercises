"""E-mail summarisation.

Deliberately unimplemented for now: `summarize()` returns `None`, and the
endpoint reports `status: "not_implemented"` so callers can build against the
final response shape today.
"""

from __future__ import annotations

from collections.abc import Sequence

from .models import Email


def summarize(emails: Sequence[Email]) -> str | None:
    """Return a natural-language summary of `emails`, or `None` if unavailable.

    TODO: implement — e.g. send the subjects/bodies to an LLM and return the
    generated digest. Keep the signature; the router only cares that a `str`
    means "summarised" and `None` means "not available yet".
    """
    return None
