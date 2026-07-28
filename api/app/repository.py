"""In-memory e-mail store, seeded from a JSON file."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from .models import Email, Priority

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "emails.json"


class EmailRepository:
    """Read-only access to the seeded e-mails, newest first."""

    def __init__(self, emails: Iterable[Email]) -> None:
        ordered = sorted(emails, key=lambda email: email.sent_at, reverse=True)
        self._by_id: dict[int, Email] = {email.id: email for email in ordered}
        self._ordered: list[Email] = ordered

    @classmethod
    def from_file(cls, path: Path | None = None) -> EmailRepository:
        """Load the seed file, or start empty when it is not there yet."""
        path = path or DEFAULT_DATA_FILE
        if not path.is_file():
            return cls([])
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(Email.model_validate(item) for item in raw)

    def list(
        self,
        q: str | None = None,
        priority: Priority | None = None,
        ids: Iterable[int] | None = None,
    ) -> list[Email]:
        wanted = set(ids) if ids is not None else None
        return [
            email
            for email in self._ordered
            if (q is None or email.matches(q))
            and (priority is None or email.priority is priority)
            and (wanted is None or email.id in wanted)
        ]

    def get(self, email_id: int) -> Email | None:
        return self._by_id.get(email_id)


@lru_cache(maxsize=1)
def get_repository() -> EmailRepository:
    """FastAPI dependency — one repository per process."""
    override = os.getenv("EMAILS_DATA_FILE")
    return EmailRepository.from_file(Path(override) if override else None)
