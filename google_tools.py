"""
google_tools.py
===============
Standalone Google integration tools (Maps / Calendar / Gmail) for Atlas.

Kept as plain functions at the project root (NOT inside the `mcp/` folder) so
importing them can't clash with the installed `mcp` pip package. Any agent can add
these to its `tools=[...]` list; ADK reads each docstring and calls the right one
ON ITS OWN based on what the student asks — no manual switch.

All keys/credentials come from environment variables only (never hard-coded).
"""

import os
import base64
from email.message import EmailMessage


def _maps_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise RuntimeError("Set GOOGLE_MAPS_API_KEY in your .env to use Maps tools.")
    return key


_GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def _google_service(api: str, version: str):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    token_path = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    if not os.path.exists(token_path):
        raise RuntimeError("No Google token. Run: python scripts/google_oauth_setup.py")
    creds = Credentials.from_authorized_user_file(token_path, _GOOGLE_SCOPES)
    return build(api, version, credentials=creds, cache_discovery=False)


# ------------------------------- Google Maps -------------------------------
def maps_travel_time(origin: str, destination: str, mode: str = "transit") -> dict:
    """Get travel time and distance between two places.

    USE THIS whenever the student asks how to get somewhere, the best way to reach
    a place, or how long a journey/commute will take — e.g. "I'm new here and want
    to reach my university, what's the best way and how long will it take?".

    Args:
        origin: where the student starts (address or place name).
        destination: where they want to go.
        mode: "transit", "driving", "walking", or "bicycling".
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

    USE THIS when the student wants to find somewhere nearby — e.g. "a quiet
    library near campus" or "cafes near the station".

    Args:
        query: kind of place (e.g. "library").
        location: area to search around (e.g. "University of X campus").
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


# ----------------------------- Google Calendar -----------------------------
def google_calendar_list(max_results: int = 10) -> list:
    """List upcoming events from the student's Google Calendar.

    USE THIS when the student asks what's on their Google Calendar / what's coming up.
    (Distinct from local task tools.)
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


def google_calendar_create(summary: str, start_iso: str, end_iso: str) -> dict:
    """Create an event on the student's Google Calendar. WRITE action — only call
    AFTER the student confirms the exact details.

    Args:
        summary: event title.
        start_iso / end_iso: ISO 8601 datetimes, e.g. "2026-07-06T09:00:00".
    """
    service = _google_service("calendar", "v3")
    body = {"summary": summary, "start": {"dateTime": start_iso},
            "end": {"dateTime": end_iso}}
    created = service.events().insert(calendarId="primary", body=body).execute()
    return {"created": created.get("summary"), "id": created.get("id"),
            "link": created.get("htmlLink")}


# -------------------------------- Gmail ------------------------------------
def gmail_search(query: str, max_results: int = 5) -> list:
    """Search the student's Gmail. USE THIS when they ask about an email they got,
    e.g. "did my professor reply about the extension?" (query 'from:professor extension')."""
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
    """Create a Gmail DRAFT (never sends). USE THIS when the student asks to email
    someone — always a draft for them to review and send themselves."""
    service = _google_service("gmail", "v1")
    msg = EmailMessage()
    msg["To"], msg["Subject"] = to, subject
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}).execute()
    return {"draft_id": draft.get("id"), "status": "draft (not sent)"}