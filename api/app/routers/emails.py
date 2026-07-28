"""`/emails` routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from ..models import Email, EmailSummary, Priority
from ..repository import EmailRepository, get_repository
from ..summarizer import summarize

router = APIRouter(prefix="/emails", tags=["emails"])

Repo = Annotated[EmailRepository, Depends(get_repository)]
SearchQuery = Annotated[
    str | None,
    Query(description="Case-insensitive search over subject and body.", examples=["bug"]),
]
PriorityFilter = Annotated[Priority | None, Query(description="Keep only this priority.")]


# Registered before `/{email_id}` — otherwise the path parameter swallows
# `/emails/summarize` and the request fails validation instead of routing here.
@router.get(
    "/summarize",
    response_model=EmailSummary,
    summary="Summarize e-mails",
    description="Summarizes the matching e-mails. The summariser itself is not implemented yet.",
)
def summarize_emails(
    repo: Repo,
    q: SearchQuery = None,
    priority: PriorityFilter = None,
    ids: Annotated[
        list[int] | None,
        Query(description="Restrict to these e-mail ids; omit for all matches."),
    ] = None,
) -> EmailSummary:
    emails = repo.list(q=q, priority=priority, ids=ids)
    summary = summarize(emails)
    return EmailSummary(
        email_ids=[email.id for email in emails],
        count=len(emails),
        summary=summary,
        status="ok" if summary is not None else "not_implemented",
    )


@router.get(
    "",
    response_model=list[Email],
    summary="List or search e-mails",
    description="Returns all e-mails, newest first. Pass `q` to search subject and body.",
)
@router.get("/", response_model=list[Email], include_in_schema=False)
def list_emails(
    repo: Repo,
    q: SearchQuery = None,
    priority: PriorityFilter = None,
) -> list[Email]:
    return repo.list(q=q, priority=priority)


@router.get(
    "/{email_id}",
    response_model=Email,
    summary="Get an e-mail by id",
    responses={status.HTTP_404_NOT_FOUND: {"description": "No e-mail with that id"}},
)
def get_email(
    repo: Repo,
    email_id: Annotated[int, Path(description="E-mail id.", examples=[1])],
) -> Email:
    email = repo.get(email_id)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"E-mail {email_id} not found",
        )
    return email
