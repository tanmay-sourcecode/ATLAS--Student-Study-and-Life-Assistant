"""
scripts/google_oauth_setup.py
=============================
Run this ONCE to authorize Atlas to use your Google Calendar + Gmail. It opens a
browser, you log in and consent, and it saves a `token.json` that the MCP server
reads later. You never put your Google password or secrets in code.

Setup before running:
  1. Go to Google Cloud Console -> create/select a project.
  2. Enable the "Google Calendar API" and "Gmail API".
  3. Configure the OAuth consent screen (External, add yourself as a test user).
  4. Create OAuth client credentials of type "Desktop app" -> download the JSON.
  5. Save that file (e.g. as `credentials.json`) and point GOOGLE_OAUTH_CREDENTIALS
     at it in your .env.

Then run:  python scripts/google_oauth_setup.py
"""

import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]

creds_file = os.environ.get("GOOGLE_OAUTH_CREDENTIALS", "credentials.json")
token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token.json")

if not os.path.exists(creds_file):
    raise SystemExit(
        f"Missing OAuth client file '{creds_file}'. Download it from Google Cloud "
        "Console (Desktop app credentials) and set GOOGLE_OAUTH_CREDENTIALS in .env."
    )

flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
creds = flow.run_local_server(port=0)  # opens a browser for consent

with open(token_path, "w") as f:
    f.write(creds.to_json())

print(f"Authorized. Saved token to {token_path}. Keep this file private (it's git-ignored).")