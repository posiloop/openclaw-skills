#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Append/read usage ledger JSONL")
    sub = p.add_subparsers(dest="cmd", required=True)

    ap = sub.add_parser("append", help="append one snapshot")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--timestamp", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--channel", default="unknown")
    ap.add_argument("--scope", default="current_session_snapshot")
    ap.add_argument("--model", required=True)
    ap.add_argument("--input-tokens", type=int, required=True)
    ap.add_argument("--output-tokens", type=int, required=True)
    ap.add_argument("--cost", default="null")
    ap.add_argument("--cost-source", default="provider_missing")
    ap.add_argument("--note", default="session_status snapshot")

    sp = sub.add_parser("summary", help="summarize ledger")
    sp.add_argument("--ledger", required=True)
    sp.add_argument("--since")
    sp.add_argument("--until")
    sp.add_argument("--group-by", choices=["model", "session", "day"], default="model")
    return p.parse_args()


def parse_iso(s):
    return datetime.fromisoformat(s)


def parse_cost(raw):
    if raw in (None, "null", "", "unknown"):
        return None
    return float(raw)


def append_entry(args):
    ledger = Path(args.ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    total = args.input_tokens + args.output_tokens
    entry = {
        "timestamp": args.timestamp,
        "session": args.session,
        "channel": args.channel,
        "scope": args.scope,
        "model": args.model,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "total_tokens": total,
        "cost": parse_cost(args.cost),
        "cost_source": args.cost_source,
        "note": args.note,
    }
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps(entry, ensure_ascii=False))


def load_entries(path):
    entries = []
    p = Path(path)
    if not p.exists():
        return entries
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def summarize(args):
    entries = load_entries(args.ledger)
    since = parse_iso(args.since) if args.since else None
    until = parse_iso(args.until) if args.until else None
    filtered = []
    for e in entries:
        ts = parse_iso(e["timestamp"])
        if since and ts < since:
            continue
        if until and ts > until:
            continue
        filtered.append(e)

    groups = {}
    for e in filtered:
        if args.group_by == "day":
            key = e["timestamp"][:10]
        else:
            key = e[args.group_by]
        g = groups.setdefault(key, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cost": 0.0, "cost_known_entries": 0, "entries": 0})
        g["input_tokens"] += e.get("input_tokens", 0)
        g["output_tokens"] += e.get("output_tokens", 0)
        g["total_tokens"] += e.get("total_tokens", 0)
        if e.get("cost") is not None:
            g["cost"] += e["cost"]
            g["cost_known_entries"] += 1
        g["entries"] += 1

    print(json.dumps({"group_by": args.group_by, "entries": len(filtered), "groups": groups}, ensure_ascii=False, indent=2))


def main():
    args = parse_args()
    if args.cmd == "append":
        append_entry(args)
    elif args.cmd == "summary":
        summarize(args)


if __name__ == "__main__":
    main()
