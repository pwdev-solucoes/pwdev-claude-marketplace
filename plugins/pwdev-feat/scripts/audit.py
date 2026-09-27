#!/usr/bin/env python3
"""pwdev-feat audit trail reader (read-only) and report exporter.

Usage (run from the project root):
  audit.py init                     create the shared schema (idempotent) and .gitignore entries
  audit.py summary | events [--plugin P] [--limit N] | decisions | artifacts | stats
  audit.py export [--pdf]           write .planning/audit-report.md (and .pdf via pandoc)
  audit.py query "<single SELECT>"  custom read-only query

Except for `init`, the database (.planning/pwdev-audit.db) is opened read-only; only a single
SELECT statement is accepted by `query`. Output is Markdown. Exit codes:
0 ok, 1 rejected query or SQL error, 2 audit disabled or database missing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

DB = Path(".planning/pwdev-audit.db")
CONFIG = Path(".planning/config.json")
REPORT_MD = Path(".planning/audit-report.md")
REPORT_PDF = Path(".planning/audit-report.pdf")

QUERIES = {
    "totals": "SELECT (SELECT COUNT(*) FROM events) AS events, (SELECT COUNT(*) FROM decisions) AS decisions, "
              "(SELECT COUNT(*) FROM artifacts WHERE status='active') AS active_artifacts, "
              "(SELECT COUNT(*) FROM config_changes) AS config_changes",
    "by_action": "SELECT action, COUNT(*) AS count FROM events GROUP BY action ORDER BY count DESC",
    "recent": "SELECT timestamp, plugin, command, agent, action, target FROM events ORDER BY id DESC LIMIT 10",
    "failed": "SELECT timestamp, plugin, command, agent, detail FROM events WHERE action='failed' ORDER BY id DESC LIMIT 5",
    "decisions": "SELECT id, timestamp, phase, decision, rationale, alternatives, "
                 "CASE reversible WHEN 1 THEN 'yes' ELSE 'no' END AS reversible FROM decisions ORDER BY id DESC",
    "artifacts_by_type": "SELECT type, COUNT(*) AS count FROM artifacts WHERE status='active' GROUP BY type ORDER BY count DESC",
    "artifacts": "SELECT path, type, phase, status, created_at, archived_at FROM artifacts ORDER BY id DESC LIMIT 200",
    "frequency": "SELECT command, COUNT(*) AS runs FROM events WHERE action='completed' GROUP BY command ORDER BY runs DESC",
    "durations": "SELECT agent, COUNT(*) AS runs, ROUND(AVG(duration_ms)/1000.0,1) AS avg_s, "
                 "ROUND(MIN(duration_ms)/1000.0,1) AS min_s, ROUND(MAX(duration_ms)/1000.0,1) AS max_s "
                 "FROM events WHERE duration_ms IS NOT NULL GROUP BY agent ORDER BY avg_s DESC",
    "models": "SELECT agent, model, COUNT(*) AS spawns FROM events WHERE action='model_resolved' GROUP BY agent, model",
    "by_plugin": "SELECT plugin, COUNT(*) AS count FROM events GROUP BY plugin ORDER BY count DESC",
    "timeline": "SELECT DATE(timestamp) AS day, COUNT(*) AS events FROM events "
                "WHERE timestamp >= datetime('now','-14 days') GROUP BY day ORDER BY day DESC",
    "success": "SELECT SUM(action='completed') AS completed, SUM(action='failed') AS failed, "
               "ROUND(100.0*SUM(action='completed')/MAX(1,SUM(action IN ('completed','failed'))),1) AS success_pct "
               "FROM events",
    "config": "SELECT timestamp, field, old_value, new_value, changed_by FROM config_changes ORDER BY id DESC",
    "period": "SELECT MIN(timestamp) AS first, MAX(timestamp) AS last FROM events",
}


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    session_id TEXT, plugin TEXT NOT NULL, command TEXT NOT NULL,
    agent TEXT, model TEXT, phase TEXT, action TEXT NOT NULL,
    target TEXT, detail TEXT, duration_ms INTEGER
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER REFERENCES events(id),
    timestamp TEXT NOT NULL DEFAULT (datetime('now')), phase TEXT NOT NULL,
    decision TEXT NOT NULL, rationale TEXT, alternatives TEXT, reversible INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER REFERENCES events(id),
    path TEXT NOT NULL, type TEXT NOT NULL, phase TEXT, status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), archived_at TEXT
);
CREATE TABLE IF NOT EXISTS config_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    field TEXT NOT NULL, old_value TEXT, new_value TEXT NOT NULL, changed_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_plugin ON events(plugin);
CREATE INDEX IF NOT EXISTS idx_events_command ON events(command);
"""
GITIGNORE_LINES = [
    ".planning/pwdev-audit.db", ".planning/pwdev-audit.db-journal", ".planning/pwdev-audit.db-wal",
    ".planning/.audit-tmp/", ".planning/audit-report.md", ".planning/audit-report.pdf",
]


def init_db() -> str:
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.execute("INSERT INTO events (plugin, command, action, target) VALUES ('pwdev-feat', 'init', 'completed', '.planning/feat/')")
    gitignore = Path(".gitignore")
    current = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    missing = [line for line in GITIGNORE_LINES if line not in current]
    if missing:
        with gitignore.open("a", encoding="utf-8") as handle:
            handle.write("\n# PWDEV audit trail (not versioned)\n" + "\n".join(missing) + "\n")
    return f"AUDIT_READY: {DB} (gitignore +{len(missing)} lines)\n"


def audit_enabled() -> bool:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8")).get("audit") is True
    except (OSError, json.JSONDecodeError, AttributeError):
        return False


def connect() -> sqlite3.Connection:
    return sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)


def run(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> tuple[list[str], list[tuple]]:
    cur = conn.execute(sql, params)
    return [d[0] for d in cur.description or []], cur.fetchall()


def md_table(cols: list[str], rows: list[tuple]) -> str:
    if not rows:
        return "_none_\n"

    def cell(v: object) -> str:
        return ("" if v is None else str(v)).replace("|", "\\|").replace("\n", " ")[:160]

    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    return "\n".join(out) + "\n"


def block(conn: sqlite3.Connection, title: str, key: str, level: str = "###") -> str:
    cols, rows = run(conn, QUERIES[key])
    return f"{level} {title}\n\n{md_table(cols, rows)}\n"


def validate_select(sql: str) -> str | None:
    stripped = sql.strip()
    if stripped.endswith(";"):
        stripped = stripped[:-1].rstrip()
    if not re.match(r"(?is)^\s*(select|with)\b", stripped):
        return None
    if ";" in stripped or re.search(r"(?i)\b(attach|detach|pragma|insert|update|delete|drop|alter|create|vacuum)\b", stripped):
        return None
    return stripped


def summary(conn) -> str:
    cols, rows = run(conn, QUERIES["totals"])
    totals = dict(zip(cols, rows[0]))
    head = " | ".join(f"**{k.replace('_', ' ')}:** {v}" for k, v in totals.items())
    return (f"## Audit Trail — Summary\n\n{head}\n\n" + block(conn, "Events by action", "by_action")
            + block(conn, "Last 10 events", "recent") + block(conn, "Failed (last 5)", "failed"))


def stats(conn) -> str:
    return ("## Statistics\n\n" + block(conn, "Command frequency", "frequency") + block(conn, "Subagent durations", "durations")
            + block(conn, "Models resolved", "models") + block(conn, "Events by plugin", "by_plugin")
            + block(conn, "Activity (last 14 days)", "timeline") + block(conn, "Success rate", "success"))


def export(conn, pdf: bool) -> str:
    project = Path.cwd().name
    try:
        branch = subprocess.run(["git", "branch", "--show-current"], text=True, capture_output=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        branch = ""
    _, period = run(conn, QUERIES["period"])
    first, last = period[0] if period else (None, None)
    body = [
        "# Audit Trail Report", "",
        f"**Project:** {project}  ", f"**Branch:** {branch or 'n/a'}  ",
        f"**Generated:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}  ", f"**Period:** {first} → {last}", "",
        summary(conn).replace("## Audit Trail — Summary", "## 1. Summary"),
        block(conn, "2. Decisions", "decisions", "##"),
        "## 3. Artifacts\n\n" + block(conn, "By type", "artifacts_by_type") + block(conn, "All (latest 200)", "artifacts"),
        stats(conn).replace("## Statistics", "## 4. Statistics"),
        block(conn, "5. Configuration history", "config", "##"),
        "*Report generated by pwdev-feat audit.py*", "",
    ]
    REPORT_MD.write_text("\n".join(body), encoding="utf-8")
    lines = [f"Markdown: {REPORT_MD}"]
    if pdf:
        if shutil.which("pandoc"):
            proc = subprocess.run(["pandoc", str(REPORT_MD), "-o", str(REPORT_PDF), "-V", "geometry:margin=2cm"],
                                  capture_output=True, text=True)
            lines.append(f"PDF: {REPORT_PDF}" if proc.returncode == 0 and REPORT_PDF.exists()
                         else f"PDF failed (pandoc exit {proc.returncode}): {proc.stderr.strip()[:200]}")
        else:
            lines.append("PDF skipped: pandoc not found (the Markdown report is complete)")
    gitignore = Path(".gitignore")
    current = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    if "audit-report" not in current:
        with gitignore.open("a", encoding="utf-8") as handle:
            handle.write("\n# PWDEV audit reports (not versioned)\n.planning/audit-report.md\n.planning/audit-report.pdf\n")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")
    for name in ("init", "summary", "decisions", "artifacts", "stats"):
        sub.add_parser(name)
    ev = sub.add_parser("events")
    ev.add_argument("--plugin")
    ev.add_argument("--limit", type=int, default=50)
    ex = sub.add_parser("export")
    ex.add_argument("--pdf", action="store_true")
    q = sub.add_parser("query")
    q.add_argument("sql")
    args = parser.parse_args(argv)
    cmd = args.cmd or "summary"

    if cmd == "init":
        print(init_db(), end="")
        return 0
    if not audit_enabled():
        print("AUDIT_DISABLED: set \"audit\": true in .planning/config.json (feat-init).")
        return 2
    if not DB.is_file():
        print(f"AUDIT_DB_MISSING: {DB} not found (feat-init creates it).")
        return 2
    try:
        with connect() as conn:
            if cmd == "summary":
                out = summary(conn)
            elif cmd == "events":
                sql = ("SELECT id, timestamp, plugin, command, agent, model, phase, action, target, "
                       "SUBSTR(detail,1,80) AS detail FROM events")
                params: tuple = ()
                if args.plugin:
                    sql += " WHERE plugin = ?"
                    params = (args.plugin,)
                sql += " ORDER BY id DESC LIMIT ?"
                cols, rows = run(conn, sql, params + (max(1, args.limit),))
                out = f"## Events (latest {max(1, args.limit)})\n\n" + md_table(cols, rows)
            elif cmd == "decisions":
                out = block(conn, "Decisions", "decisions", "##")
            elif cmd == "artifacts":
                out = "## Artifacts\n\n" + block(conn, "By type", "artifacts_by_type") + block(conn, "All (latest 200)", "artifacts")
            elif cmd == "stats":
                out = stats(conn)
            elif cmd == "export":
                out = export(conn, args.pdf)
            else:
                sql = validate_select(args.sql)
                if sql is None:
                    print("REJECTED: only a single read-only SELECT statement is allowed.")
                    return 1
                cols, rows = run(conn, sql)
                out = md_table(cols, rows) + (
                    "\nTables: events, decisions, artifacts, config_changes — see references/audit-schema.md\n")
    except sqlite3.Error as exc:
        print(f"SQL_ERROR: {exc}")
        return 1
    print(out, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
