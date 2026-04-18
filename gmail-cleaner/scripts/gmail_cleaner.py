#!/usr/bin/env python3
"""
Gmail Cleaner - Scan inbox for spam and analyze spam folder for rule updates.

Usage:
  python3 gmail_cleaner.py scan     # Mode A: scan inbox and list spam candidates
  python3 gmail_cleaner.py analyze  # Mode B: analyze spam folder and suggest rule updates
"""

import sys
import json
import re
import base64
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts dir to path for gmail_auth import
sys.path.insert(0, str(Path(__file__).parent))
from gmail_auth import get_gmail_service, BASE_DIR

BLACKLIST_FILE = BASE_DIR / "blacklist.json"
FEATURES_FILE = BASE_DIR / "spam_features.json"
MAX_RESULTS = 200  # Max emails to fetch per request


# ─── File helpers ────────────────────────────────────────────────────────────

def load_json(path: Path, default: dict) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 已儲存：{path}")


def default_blacklist():
    return {"version": "1.0", "senders": [], "sender_patterns": []}


def default_features():
    return {
        "version": "1.0",
        "subject_keywords": [],
        "subject_patterns": [],
        "body_keywords": [],
        "combined_rules": []
    }


# ─── Gmail API helpers ────────────────────────────────────────────────────────

def list_messages(service, label_ids=None, max_results=MAX_RESULTS):
    """List messages with given label(s)."""
    msgs = []
    params = {"userId": "me", "maxResults": min(max_results, 500)}
    if label_ids:
        params["labelIds"] = label_ids
    result = service.users().messages().list(**params).execute()
    msgs.extend(result.get("messages", []))
    while "nextPageToken" in result and len(msgs) < max_results:
        result = service.users().messages().list(
            **params, pageToken=result["nextPageToken"]
        ).execute()
        msgs.extend(result.get("messages", []))
    return msgs[:max_results]


def get_message_meta(service, msg_id):
    """Get sender, subject, date, snippet, and internal timestamp for a message."""
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "Subject", "Date"]
    ).execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    return {
        "id": msg_id,
        "from": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "snippet": msg.get("snippet", ""),
        "internal_date": int(msg.get("internalDate", 0))
    }


def get_message_body_snippet(service, msg_id, max_chars=500):
    """Get first max_chars of message body text."""
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()
    return _extract_text(msg["payload"], max_chars)


def _extract_text(payload, max_chars):
    """Recursively extract plain text from message payload."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")[:max_chars]
    for part in payload.get("parts", []):
        text = _extract_text(part, max_chars)
        if text:
            return text
    return ""


def trash_messages(service, msg_ids):
    """Move messages to trash."""
    for mid in msg_ids:
        service.users().messages().trash(userId="me", id=mid).execute()


# ─── Spam matching ────────────────────────────────────────────────────────────

def is_spam(meta, blacklist, features) -> tuple[bool, str]:
    """Return (is_spam, matched_rule_description)."""
    sender = meta["from"].lower()
    subject = meta["subject"]
    snippet = meta["snippet"]

    # Blacklist: exact sender
    for s in blacklist.get("senders", []):
        s = s.lower()
        if s.startswith("@"):
            if sender.endswith(s):
                return True, f"黑名單網域 {s}"
        elif s in sender:
            return True, f"黑名單寄件者 {s}"

    # Blacklist: sender patterns
    for pat in blacklist.get("sender_patterns", []):
        if re.search(pat, sender, re.IGNORECASE):
            return True, f"黑名單規則 {pat}"

    # Subject keywords
    for kw in features.get("subject_keywords", []):
        if kw.lower() in subject.lower():
            return True, f"主旨關鍵字「{kw}」"

    # Subject patterns
    for pat in features.get("subject_patterns", []):
        if re.search(pat, subject, re.IGNORECASE):
            return True, f"主旨規則 {pat}"

    # Body keywords
    for kw in features.get("body_keywords", []):
        if kw.lower() in snippet.lower():
            return True, f"內文關鍵字「{kw}」"

    # Combined rules
    for rule in features.get("combined_rules", []):
        if _check_combined(rule, sender, subject, snippet):
            return True, f"複合規則「{rule.get('description', '')}」"

    return False, ""


def _check_combined(rule, sender, subject, snippet):
    """Check a combined rule."""
    # subject_contains_any
    for kw in rule.get("subject_contains_any", []):
        if kw.lower() not in subject.lower():
            return False
        # sender_domain_not_in: if sender is in trusted list, skip
        for trusted in rule.get("sender_domain_not_in", []):
            if trusted.lower() in sender:
                return False
        return True
    return False


# ─── Display helpers ─────────────────────────────────────────────────────────

def truncate(s, n):
    return s[:n-1] + "…" if len(s) > n else s.ljust(n)


def print_spam_table(candidates):
    """Print ASCII table of spam candidates."""
    col_widths = [4, 30, 34, 12, 18]
    headers = ["#", "寄件者", "主旨", "日期", "匹配規則"]
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    row_fmt = "|" + "|".join(" {:" + str(w) + "} " for w in col_widths) + "|"

    print(sep)
    print(row_fmt.format(*[truncate(h, w) for h, w in zip(headers, col_widths)]))
    print(sep)
    for i, c in enumerate(candidates, 1):
        # Parse date
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(c["date"])
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = c["date"][:10]

        print(row_fmt.format(
            truncate(str(i), col_widths[0]),
            truncate(c["from"], col_widths[1]),
            truncate(c["subject"], col_widths[2]),
            truncate(date_str, col_widths[3]),
            truncate(c["matched_rule"], col_widths[4]),
        ))
        print(sep)


# ─── Mode A: Scan inbox ───────────────────────────────────────────────────────

def mode_scan():
    print("=== 模式 A：掃描 Inbox 垃圾郵件 ===\n")
    service = get_gmail_service()
    blacklist = load_json(BLACKLIST_FILE, default_blacklist())
    features = load_json(FEATURES_FILE, default_features())

    print("正在讀取 inbox 郵件（最多 200 封）...")
    msgs = list_messages(service, label_ids=["INBOX"])
    if not msgs:
        print("Inbox 是空的。")
        return

    print(f"共 {len(msgs)} 封，正在比對規則...")
    candidates = []
    for i, m in enumerate(msgs, 1):
        if i % 20 == 0:
            print(f"  處理中 {i}/{len(msgs)}...")
        meta = get_message_meta(service, m["id"])
        spam, rule = is_spam(meta, blacklist, features)
        if spam:
            meta["matched_rule"] = rule
            candidates.append(meta)

    if not candidates:
        print("\n沒有找到符合規則的垃圾郵件。")
        return

    print(f"\n找到 {len(candidates)} 封候選垃圾郵件：\n")
    print_spam_table(candidates)

    print("\n請輸入要刪除的郵件編號（例如：1,3,5 或 all 或 none）：", end=" ")
    choice = input().strip().lower()

    if choice == "none" or choice == "":
        print("已取消，未刪除任何郵件。")
        return

    if choice == "all":
        to_delete = candidates
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            to_delete = [candidates[i] for i in indices if 0 <= i < len(candidates)]
        except (ValueError, IndexError):
            print("輸入格式錯誤，已取消。")
            return

    print(f"\n確認刪除 {len(to_delete)} 封郵件？(y/n)：", end=" ")
    confirm = input().strip().lower()
    if confirm != "y":
        print("已取消。")
        return

    print("正在移至垃圾桶...")
    trash_messages(service, [m["id"] for m in to_delete])
    print(f"[OK] 已刪除 {len(to_delete)} 封垃圾郵件。")


# ─── Mode B: Analyze recent spam/trash frequency ─────────────────────────────

STOPWORDS = {
    "the", "is", "and", "or", "to", "a", "of", "in", "for", "re", "fw",
    "you", "your", "we", "our", "this", "that", "with", "from", "has",
    "have", "been", "will", "can", "an", "at", "it", "be", "on", "by",
    "as", "are", "was", "not", "all", "if", "so", "do", "my", "me",
    "no", "up", "his", "her", "its", "hi", "hello", "dear", "please",
}

ANALYZE_DAYS = 30
TOP_N = 20
BODY_STOPWORDS = {
    "https", "http", "www", "com", "net", "org", "io", "html", "htm",
    "img", "png", "jpg", "jpeg", "gif", "css", "td", "tr", "href",
    "src", "utm", "utm_source", "utm_medium", "utm_campaign", "view",
    "email", "click", "here", "link", "links", "top", "message",
    "unsubscribe", "header", "footer", "nbsp", "zwnj", "amp", "3d",
    "4_", "mxb"
}
BODY_MIN_LEN = 2
BODY_MAX_LEN = 8


def _is_blacklisted_sender(sender, blacklist_senders):
    sender = sender.lower()
    for s in blacklist_senders:
        s = s.lower()
        if s.startswith("@"):
            if sender.endswith(s):
                return True
        elif s in sender:
            return True
    return False


def _print_ranked(title, items, formatter):
    print(f"\n【{title}】")
    if not items:
        print("  無資料")
        return
    for i, item in enumerate(items, 1):
        print(f"  {i}. {formatter(item)}")


def mode_analyze():
    print("=== 模式 B：分析近一個月垃圾信箱高頻項目 ===\n")
    service = get_gmail_service()
    blacklist = load_json(BLACKLIST_FILE, default_blacklist())
    blacklist_senders = blacklist.get("senders", [])

    print("正在讀取垃圾筒 + 垃圾信箱（最多各 100 封）...")
    trash_msgs = list_messages(service, label_ids=["TRASH"], max_results=100)
    spam_msgs = list_messages(service, label_ids=["SPAM"], max_results=100)

    seen = set()
    msgs = []
    for m in trash_msgs + spam_msgs:
        if m["id"] not in seen:
            seen.add(m["id"])
            msgs.append(m)

    if not msgs:
        print("垃圾筒與垃圾信箱都是空的。")
        return

    cutoff_ts = int((datetime.now().astimezone() - timedelta(days=ANALYZE_DAYS)).timestamp() * 1000)
    recent_metas = []
    print(f"正在篩選近 {ANALYZE_DAYS} 天郵件...")
    for m in msgs:
        meta = get_message_meta(service, m["id"])
        if meta["internal_date"] >= cutoff_ts:
            recent_metas.append(meta)

    if not recent_metas:
        print(f"近 {ANALYZE_DAYS} 天內沒有垃圾筒或垃圾信箱郵件。")
        return

    filtered_metas = [m for m in recent_metas if not _is_blacklisted_sender(m["from"], blacklist_senders)]
    excluded_count = len(recent_metas) - len(filtered_metas)

    if not filtered_metas:
        print(f"近 {ANALYZE_DAYS} 天的垃圾郵件都已被目前黑名單覆蓋，沒有剩餘樣本可分析。")
        return

    print(
        f"近 {ANALYZE_DAYS} 天共 {len(recent_metas)} 封，排除黑名單寄件者後剩 {len(filtered_metas)} 封，"
        f"排除 {excluded_count} 封。正在分析最高頻 email、主旨關鍵字、內文關鍵字...\n"
    )

    email_counts = {}
    subject_kw_counts = {}
    body_kw_counts = {}

    for i, meta in enumerate(filtered_metas, 1):
        if i % 20 == 0:
            print(f"  處理中 {i}/{len(filtered_metas)}...")

        body = get_message_body_snippet(service, meta["id"], max_chars=800)

        sender_raw = meta["from"].lower()
        addr_match = re.search(r"[\w\.\+\-]+@[\w\.\-]+", sender_raw)
        if addr_match:
            addr = addr_match.group(0)
            email_counts[addr] = email_counts.get(addr, 0) + 1

        subj_words = re.findall(r"[\w\u4e00-\u9fff]{2,}", meta["subject"])
        for w in subj_words:
            wl = w.lower()
            if wl not in STOPWORDS and not w.isdigit():
                subject_kw_counts[w] = subject_kw_counts.get(w, 0) + 1

        body_words = re.findall(r"[\w\u4e00-\u9fff]{2,}", body)
        for w in body_words:
            wl = w.lower()
            if (
                wl not in STOPWORDS
                and wl not in BODY_STOPWORDS
                and not w.isdigit()
                and BODY_MIN_LEN <= len(w) <= BODY_MAX_LEN
                and not wl.startswith("http")
                and "." not in w
                and "@" not in w
                and not re.fullmatch(r"[a-z0-9_\-]+", wl)
            ):
                body_kw_counts[w] = body_kw_counts.get(w, 0) + 1

    top_emails = sorted(email_counts.items(), key=lambda x: (-x[1], x[0]))[:TOP_N]
    top_subjects = sorted(subject_kw_counts.items(), key=lambda x: (-x[1], x[0]))[:TOP_N]
    top_bodies = sorted(body_kw_counts.items(), key=lambda x: (-x[1], x[0]))[:TOP_N]

    print(f"分析範圍：近 {ANALYZE_DAYS} 天，共 {len(filtered_metas)} 封郵件（已排除黑名單寄件者）")
    _print_ranked("最高頻 email", top_emails, lambda x: f"{x[0]}  （{x[1]} 次）")
    _print_ranked("最高頻主旨關鍵字", top_subjects, lambda x: f"「{x[0]}」  （{x[1]} 次）")
    _print_ranked("最高頻內文關鍵字", top_bodies, lambda x: f"「{x[0]}」  （{x[1]} 次）")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("scan", "analyze"):
        print("用法：python3 gmail_cleaner.py <scan|analyze>")
        print("  scan    — 模式 A：掃描 inbox 垃圾郵件")
        print("  analyze — 模式 B：分析垃圾信箱，更新黑名單/特徵")
        sys.exit(1)

    mode = sys.argv[1]
    try:
        if mode == "scan":
            mode_scan()
        elif mode == "analyze":
            mode_analyze()
    except KeyboardInterrupt:
        print("\n\n已中斷。")
    except FileNotFoundError as e:
        print(f"\n[錯誤] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
