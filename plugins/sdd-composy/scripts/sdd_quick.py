#!/usr/bin/env python3
"""Authoritative, side-effect-free eligibility gate for the SDD quick path."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def evaluate(contract: dict) -> dict:
    if not isinstance(contract, dict): return {"decision": "ESCALATE", "reasons": ["invalid contract"]}
    quick = contract.get("quick") if isinstance(contract.get("quick"), dict) else contract
    files, commands = quick.get("allowed_files", quick.get("allowed_paths", [])), quick.get("verification_commands", [])
    reasons = []
    if not isinstance(files, list) or len(files) > 5: reasons.append("more than five implementation files")
    if not isinstance(commands, list) or not commands or any(not isinstance(c, str) or not c.strip() for c in commands): reasons.append("unknown verification")
    for field, label in (("architecture", "architecture work"), ("migration", "migration work"), ("destructive", "destructive work"), ("scope_expansion", "scope expansion")):
        if quick.get(field) is True or contract.get(field) is True: reasons.append(label)
    return {"decision": "ESCALATE" if reasons else "QUICK", "reasons": reasons}

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("contract", type=Path); args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.contract.read_text(encoding="utf-8"))); print(json.dumps(result, sort_keys=True)); return 0 if result["decision"] == "QUICK" else 2
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"decision": "ESCALATE", "reasons": [str(exc)]}, sort_keys=True)); return 2
if __name__ == "__main__": raise SystemExit(main())
