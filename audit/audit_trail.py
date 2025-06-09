# audit/audit_trail.py
"""
Audit Trail Toolkit
====================

Utility module to read and parse structured audit logs from decisions/.
Supports:
- loading daily audit logs
- searching by intent_id
- aggregating by executor type or rejection reason
"""

import os
import json
import glob
from collections import defaultdict

def load_decision_log(client_id: str, date_str: str = None):
    base_path = f"clients/{client_id}/audit/decisions/"
    if date_str:
        path = os.path.join(base_path, f"{date_str}.jsonl")
    else:
        files = sorted(glob.glob(base_path + "*.jsonl"))
        if not files:
            return []
        path = files[-1]  # latest log file

    records = []
    with open(path, "r") as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except:
                continue
    return records

def find_by_intent_id(client_id: str, intent_id: str):
    base_path = f"clients/{client_id}/audit/decisions/"
    matches = []
    for file in sorted(glob.glob(base_path + "*.jsonl")):
        with open(file) as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get("intent", {}).get("intent_id") == intent_id:
                        matches.append(data)
                except:
                    continue
    return matches

def summarize_executor_usage(records):
    counter = defaultdict(int)
    for rec in records:
        etype = rec.get("executor_type", "unknown")
        counter[etype] += 1
    return dict(counter)

def summarize_rejection_reasons(records):
    reasons = defaultdict(int)
    for rec in records:
        if rec.get("execution", {}).get("status") == "rejected":
            reason = rec.get("approval", {}).get("reason_code", "UNKNOWN")
            reasons[reason] += 1
    return dict(reasons)

def list_all_trade_ids(records):
    return [(r.get("intent", {}).get("intent_id"), r.get("execution", {}).get("status")) for r in records]