# E-mail API

Read-only FastAPI backend over an inbox of e-mails.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive docs: <http://localhost:8000/docs>

## Endpoints

| Method | Path                | Notes                                                       |
| ------ | ------------------- | ----------------------------------------------------------- |
| GET    | `/emails`           | All e-mails, newest first. `?q=` searches subject + body, `?priority=` filters. Trailing slash also works. |
| GET    | `/emails/{id}`      | One e-mail; `404` if the id is unknown.                       |
| GET    | `/emails/summarize` | Summary of the matching e-mails. Accepts `q`, `priority`, `ids`. **Stub** — see below. |
| GET    | `/health`           | Liveness probe.                                               |

`/emails/summarize` is registered before `/emails/{id}` so the path parameter
does not swallow it.

## Data contract

```json
{
  "id": 1,
  "from": "test@gmail.com",
  "to": "test@gmail.com",
  "subject": "Critical Bug",
  "body": "Email text",
  "priority": "critical",
  "date": "28-Jul-2026",
  "time": "13:53",
  "highPriority": true
}
```

- `priority` is one of `low` / `medium` / `critical`.
- `date` is `DD-Mon-YYYY`, `time` is 24-hour `HH:MM`.
- `highPriority` is optional in the source data — when absent it is derived as
  `priority == "critical"`.

## Data source

E-mails are loaded once at startup from `data/emails.json` (a JSON array of the
objects above). Set `EMAILS_DATA_FILE` to point elsewhere. **There is no seed
file yet** — until one exists the API answers `200` with an empty list, so
clients can be built against it today.

## Summarization

`app/summarizer.py::summarize()` is intentionally unimplemented: it returns
`None`, and the endpoint reports the final response shape with
`"summary": null, "status": "not_implemented"`. Fill in the function body — the
router needs no changes once it returns a string.

## Layout

```
app/
  main.py            FastAPI app, CORS (defaults to http://localhost:3000)
  models.py          Email / EmailSummary contract
  repository.py      in-memory store + search
  summarizer.py      summarization stub
  routers/emails.py  /emails routes
data/emails.json     seed data (not present yet)
```
