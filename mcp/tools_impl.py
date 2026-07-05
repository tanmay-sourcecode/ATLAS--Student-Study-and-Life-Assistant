"""
mcp/tools_impl.py
=================
Shared implementations of Atlas's real-world tools (Google Maps / Calendar / Gmail).

These are plain Python functions so BOTH the MCP server (mcp/server.py) AND the
ADK agents can use the exact same logic. That's the key to autonomous use:

    ADK gives every function in an agent's `tools=[...]` list to the model, and the
    model decides WHEN to call each one by reading its DOCSTRING. So the docstrings
    below are written as "use this when the student ..." — that's what makes Atlas
    call the tool on its own, without anyone flipping a switch.

Secrets come from environment variables only (never hard-coded).
"""

import os
import base64
from email.message import EmailMessage


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _maps_key() -> str:
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        raise RuntimeError("Set GOOGLE_MAPS_API_KEY in your .env to use Maps tools.")
    return key


GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def _google_service(api: str, version: str):
    """Build an authenticated Google client from the saved OAuth token."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token.json")
    if not os.path.exists(token_path):
        raise RuntimeError("No Google token. Run: python scripts/google_oauth_setup.py")
    creds = Credentials.from_authorized_user_file(token_path, GOOGLE_SCOPES)
    return build(api, version, credentials=creds, cache_discovery=False)


# --------------------------------------------------------------------------
# Google Maps
# --------------------------------------------------------------------------
def maps_travel_time(origin: str, destination: str, mode: str = "transit") -> dict:
    """Get travel time and distance between two places.

    USE THIS whenever the student asks how to get somewhere, the best way to
    reach a place, or how long a journey/commute will take — for example
    "how do I get to the university and how long will it take?" or
    "what's the fastest way to campus from my address?".

    Args:
        origin: where the student is starting from (address or place name).
        destination: where they want to go.
        mode: one of "transit", "driving", "walking", "bicycling".
    """
    import requests
    r = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        params={"origins": origin, "destinations": destination,
                "mode": mode, "key": _maps_key()},
        timeout=15,
    )
    data = r.json()
    try:
        el = data["rows"][0]["elements"][0]
        return {"mode": mode, "duration": el["duration"]["text"],
                "distance": el["distance"]["text"]}
    except (KeyError, IndexError):
        return {"error": "No route found", "status": data.get("status")}


def maps_find_nearby(query: str, location: str) -> list:
    """Find places of a given type near a location.

    USE THIS when the student wants to find somewhere nearby — e.g.
    "a quiet library near campus", "cafes near the station", "printing shop
    close to the university".

    Args:
        query: the kind of place to find (e.g. "library", "cafe").
        location: the area to search around (e.g. "University of X campus").
    """
    import requests
    r = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={"query": f"{query} near {location}", "key": _maps_key()},
        timeout=15,
    )
    results = r.json().get("results", [])[:5]
    return [{"name": p.get("name"), "address": p.get("formatted_address"),
             "rating": p.get("rating")} for p in results]


# --------------------------------------------------------------------------
# Google Calendar
# --------------------------------------------------------------------------
def calendar_list_events(max_results: int = 10) -> list:
    """List the student's upcoming Google Calendar events.

    USE THIS when the student asks what's on their calendar, what's coming up,
    or when their next class/meeting is.
    """
    from datetime import datetime, timezone
    service = _google_service("calendar", "v3")
    now = datetime.now(timezone.utc).isoformat()
    events = service.events().list(
        calendarId="primary", timeMin=now, maxResults=max_results,
        singleEvents=True, orderBy="startTime",
    ).execute().get("items", [])
    return [{"summary": e.get("summary"),
             "start": e["start"].get("dateTime", e["start"].get("date"))}
            for e in events]


def calendar_create_event(summary: str, start_iso: str, end_iso: str) -> dict:
    """Create an event on the student's Google Calendar.

    USE THIS when the student asks to schedule/block time (e.g. "block 2 hours
    to study tomorrow morning"). This CHANGES their calendar, so only call it
    AFTER the student has confirmed the exact details.

    Args:
        summary: event title.
        start_iso / end_iso: ISO 8601 datetimes, e.g. "2026-07-06T09:00:00".
    """
    service = _google_service("calendar", "v3")
    body = {"summary": summary,
            "start": {"dateTime": start_iso},
            "end": {"dateTime": end_iso}}
    created = service.events().insert(calendarId="primary", body=body).execute()
    return {"created": created.get("summary"), "id": created.get("id"),
            "link": created.get("htmlLink")}


# --------------------------------------------------------------------------
# Gmail
# --------------------------------------------------------------------------
def gmail_search(query: str, max_results: int = 5) -> list:
    """Search the student's Gmail.

    USE THIS when the student asks about an email they received — e.g.
    "did my professor reply about the extension?" (query: "from:professor extension").
    """
    service = _google_service("gmail", "v1")
    msgs = service.users().messages().list(
        userId="me", q=query, maxResults=max_results).execute().get("messages", [])
    out = []
    for m in msgs:
        full = service.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["Subject", "From"]).execute()
        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        out.append({"from": headers.get("From"), "subject": headers.get("Subject")})
    return out


def gmail_create_draft(to: str, subject: str, body: str) -> dict:
    """Create a Gmail DRAFT (never sends).

    USE THIS when the student asks to email someone. Always create a draft for
    them to review and send themselves — Atlas never sends automatically.
    """
    service = _google_service("gmail", "v1")
    msg = EmailMessage()
    msg["To"], msg["Subject"] = to, subject
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}).execute()
    return {"draft_id": draft.get("id"), "status": "draft (not sent)"}