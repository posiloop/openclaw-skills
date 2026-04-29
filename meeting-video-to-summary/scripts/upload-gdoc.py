#!/usr/bin/env python3
"""Upload a local file to Google Drive, converting to a Google Doc.

Usage:
    upload-gdoc.py <local-file> <parent-folder-id> <doc-title>

First run triggers OAuth consent in the browser; subsequent runs reuse
the cached token at ~/.config/google-oauth/token.json.

Environment:
    GOOGLE_OAUTH_CLIENT  path to credentials.json from GCP Console
                         (default: ~/.config/google-oauth/credentials.json)
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CONFIG_DIR = Path(os.environ.get("GOOGLE_OAUTH_DIR", str(Path.home() / ".config" / "google-oauth")))
CLIENT_FILE = Path(os.environ.get("GOOGLE_OAUTH_CLIENT", str(CONFIG_DIR / "credentials.json")))
TOKEN_FILE = CONFIG_DIR / "token.json"


def get_credentials() -> Credentials:
    creds: Credentials | None = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not CLIENT_FILE.exists():
            sys.exit(
                f"[error] OAuth client file not found: {CLIENT_FILE}\n"
                "Create an OAuth 2.0 Client ID (Desktop app) in GCP Console and save it there."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json())
    os.chmod(TOKEN_FILE, 0o600)
    return creds


def detect_source_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".html": "text/html",
        ".htm": "text/html",
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }.get(suffix, "text/plain")


def upload(local_path: Path, parent_id: str, title: str) -> str:
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [parent_id],
    }
    media = MediaFileUpload(str(local_path), mimetype=detect_source_mime(local_path))
    file = service.files().create(body=metadata, media_body=media, fields="id,webViewLink").execute()
    return file["webViewLink"]


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("Usage: upload-gdoc.py <local-file> <parent-folder-id> <doc-title>")
    local = Path(sys.argv[1])
    parent = sys.argv[2]
    title = sys.argv[3]
    if not local.is_file():
        sys.exit(f"[error] file not found: {local}")
    url = upload(local, parent, title)
    print(url)


if __name__ == "__main__":
    main()
