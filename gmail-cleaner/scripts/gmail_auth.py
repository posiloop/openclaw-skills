#!/usr/bin/env python3
"""Gmail OAuth authentication module."""

from pathlib import Path

BASE_DIR = Path.home() / "Wu" / "gmail"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def _save_token(creds):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())


def _run_local_oauth_flow(client_secrets_file, scopes):
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_file), scopes)
    return flow.run_local_server(port=0)


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"找不到 credentials.json，請參考設定指南：\n"
            f"skills/gmail-cleaner/references/setup-guide.md\n"
            f"並將檔案放置到：{CREDENTIALS_FILE}"
        )

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.valid:
        return build("gmail", "v1", credentials=creds)

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
            return build("gmail", "v1", credentials=creds)
        except RefreshError as e:
            if TOKEN_FILE.exists():
                TOKEN_FILE.unlink()
            raise RuntimeError(
                "token.json 的 refresh token 已失效或被撤銷，無法自動續期。"
                "請重新做一次 OAuth 授權以產生新的 token.json。"
            ) from e

    raise RuntimeError(
        "目前尚未取得可用的 token.json。"
        "第一次授權或 token 失效後，需要在執行腳本的同一台電腦上完成一次 OAuth 登入。"
    )


def reauthorize_gmail():
    """Run OAuth flow interactively and persist token.json."""
    creds = _run_local_oauth_flow(CREDENTIALS_FILE, SCOPES)
    _save_token(creds)
    return creds


if __name__ == "__main__":
    reauthorize_gmail()
    print(f"[OK] 已更新授權 token: {TOKEN_FILE}")
