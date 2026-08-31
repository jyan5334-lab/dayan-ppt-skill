#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
from pathlib import Path


DEFAULT_REGISTRY = Path(__file__).resolve().parent.parent / "references" / "learning-cases.jsonl"
FORBIDDEN_KEYS = {"client_name", "customer_name", "source_paths", "raw_data", "password", "token", "secret", "contact", "template_file", "template_screenshot"}
PROMOTION_STATUSES = {"candidate", "validated", "promoted", "rejected"}
RECORD_STATUSES = {"candidate", "accepted", "rejected"}
COMPACT_LIST_FIELDS = {
    "input_types",
    "accepted_patterns",
    "rejected_patterns",
    "stable_rules",
    "style_variables",
    "data_rules",
}
MAX_LIST_ITEMS = 8
MAX_ITEM_LENGTH = 200


def load_registry(path: Path):
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid registry line {number}: {exc}") from exc
    return records


def walk(value, key=""):
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            yield child_key, child_value
            yield from walk(child_value, child_key)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child, key)


def ordered_unique(values):
    result = []
    seen = set()
    for value in values or []:
        if not isinstance(value, str):
            result.append(value)
            continue
        cleaned = " ".join(value.split())
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def normalize(record):
    normalized = json.loads(json.dumps(record, ensure_ascii=False))
    for field in COMPACT_LIST_FIELDS:
        if field in normalized and isinstance(normalized[field], list):
            normalized[field] = ordered_unique(normalized[field])[:MAX_LIST_ITEMS]
    return normalized


def validate(record):
    errors = []
    required = ["case_id", "date", "status", "classification", "accepted_patterns", "rejected_patterns", "stable_rules", "style_variables", "data_rules", "qa", "privacy"]
    for key in required:
        if key not in record:
            errors.append(f"missing {key}")
    if not re.fullmatch(r"[a-z0-9-]{8,120}", str(record.get("case_id", ""))):
        errors.append("case_id must use lowercase letters, digits, and hyphens")
    try:
        dt.date.fromisoformat(record.get("date", ""))
    except ValueError:
        errors.append("date must be YYYY-MM-DD")
    record_status = record.get("status")
    if record_status not in RECORD_STATUSES:
        errors.append("status must be candidate, accepted, or rejected")

    classification = record.get("classification") or {}
    if not re.fullmatch(r"I(0[1-9]|1[0-5])", str(classification.get("industry_code", ""))):
        errors.append("industry_code must be I01-I15")
    if not re.fullmatch(r"H(0[1-9]|1[0-2])", str(classification.get("scenario_code", ""))):
        errors.append("scenario_code must be H01-H12")
    if (record.get("privacy") or {}).get("contains_client_data") is not False:
        errors.append("contains_client_data must be false")

    qa = record.get("qa") or {}
    if record_status == "candidate":
        if qa.get("delivery_complete") is not True:
            errors.append("candidate requires qa.delivery_complete=true")
        score = qa.get("total_score")
        if not isinstance(score, (int, float)) or score < 85 or score > 100:
            errors.append("candidate requires qa.total_score of 85-100")
        if qa.get("overflow_free") is not True:
            errors.append("candidate requires qa.overflow_free=true")
        if qa.get("archive_valid") is not True:
            errors.append("candidate requires qa.archive_valid=true")
        if qa.get("hard_failures") not in ([], None):
            errors.append("candidate requires qa.hard_failures to be empty")
        if qa.get("user_accepted") is True:
            errors.append("use status=accepted when qa.user_accepted=true")
    if record_status == "accepted" and qa.get("user_accepted") is not True:
        errors.append("accepted records require qa.user_accepted=true")

    if not any(record.get(key) for key in ("accepted_patterns", "rejected_patterns", "stable_rules")):
        errors.append("learning record must contain at least one reusable or rejected pattern")
    for field in COMPACT_LIST_FIELDS:
        values = record.get(field) or []
        if not isinstance(values, list):
            errors.append(f"{field} must be a list")
            continue
        if len(values) > MAX_LIST_ITEMS:
            errors.append(f"{field} must contain no more than {MAX_LIST_ITEMS} items")
        for value in values:
            if not isinstance(value, str):
                errors.append(f"{field} items must be strings")
            elif len(value) > MAX_ITEM_LENGTH:
                errors.append(f"{field} items must be no longer than {MAX_ITEM_LENGTH} characters")

    supersedes = record.get("supersedes")
    if supersedes is not None and not re.fullmatch(r"[a-z0-9-]{8,120}", str(supersedes)):
        errors.append("supersedes must be a valid case_id")

    promotion = record.get("promotion") or {"status": "candidate"}
    status = promotion.get("status")
    if status not in PROMOTION_STATUSES:
        errors.append("promotion.status must be candidate, validated, promoted, or rejected")
    if status in {"validated", "promoted"}:
        score = (record.get("qa") or {}).get("total_score")
        if not isinstance(score, (int, float)) or score < 85 or score > 100:
            errors.append("validated/promoted records require qa.total_score of 85-100")
        case_ids = promotion.get("supporting_case_ids") or []
        if len(set(case_ids)) < 3:
            errors.append("validated/promoted records require three distinct supporting_case_ids")
        if promotion.get("human_confirmed") is not True:
            errors.append("validated/promoted records require promotion.human_confirmed=true")

    for key, value in walk(record):
        if key in FORBIDDEN_KEYS:
            errors.append(f"forbidden sensitive key: {key}")
        if isinstance(value, str):
            if value.startswith("/") or re.match(r"^[A-Za-z]:\\", value):
                errors.append("absolute paths are forbidden")
            if len(value) > 500:
                errors.append("learning entries must be abstract, not raw source text")
    return sorted(set(errors))


def query(args) -> int:
    records = load_registry(Path(args.registry))
    superseded = {record.get("supersedes") for record in records if record.get("supersedes")}
    matches = []
    for record in records:
        if record.get("case_id") in superseded:
            continue
        classification = record.get("classification") or {}
        if args.industry and classification.get("industry_code") != args.industry:
            continue
        if args.scenario and classification.get("scenario_code") != args.scenario:
            continue
        if record.get("status") == "rejected" and not args.include_rejected:
            continue
        promotion = (record.get("promotion") or {}).get("status", "candidate")
        confidence = "stable" if record.get("status") == "accepted" or promotion in {"validated", "promoted"} else "advisory"
        if args.stable_only and confidence != "stable":
            continue
        annotated = dict(record)
        annotated["confidence"] = confidence
        matches.append(annotated)

    def evidence_rank(item):
        promotion = (item.get("promotion") or {}).get("status")
        if promotion == "promoted":
            return 4
        if promotion == "validated":
            return 3
        if item.get("status") == "accepted":
            return 2
        if item.get("status") == "candidate":
            return 1
        return 0

    matches.sort(
        key=lambda item: (
            evidence_rank(item),
            item.get("date", ""),
            item.get("case_id", ""),
        ),
        reverse=True,
    )
    matches = matches[: args.limit]

    stable_patterns = []
    stable_rules = []
    advisory_patterns = []
    avoid_patterns = []
    stable_data_rules = []
    advisory_data_rules = []
    style_variables = []
    for record in matches:
        if record["confidence"] == "stable":
            stable_patterns.extend(record.get("accepted_patterns") or [])
            stable_rules.extend(record.get("stable_rules") or [])
            stable_data_rules.extend(record.get("data_rules") or [])
        else:
            advisory_patterns.extend(record.get("accepted_patterns") or [])
            advisory_patterns.extend(record.get("stable_rules") or [])
            advisory_data_rules.extend(record.get("data_rules") or [])
        avoid_patterns.extend(record.get("rejected_patterns") or [])
        style_variables.extend(record.get("style_variables") or [])

    payload = {
        "matches": len(matches),
        "branch_status": "existing" if matches else "new",
        "guidance": {
            "stable_patterns": ordered_unique(stable_patterns),
            "stable_rules": ordered_unique(stable_rules),
            "advisory_patterns": ordered_unique(advisory_patterns),
            "avoid_patterns": ordered_unique(avoid_patterns),
            "stable_data_rules": ordered_unique(stable_data_rules),
            "advisory_data_rules": ordered_unique(advisory_data_rules),
            "style_variables": ordered_unique(style_variables),
        },
        "records": matches,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def record(args) -> int:
    registry = Path(args.registry)
    candidate = normalize(json.loads(Path(args.file).read_text(encoding="utf-8")))
    errors = validate(candidate)
    if errors:
        print(json.dumps({"status": "blocked", "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    records = load_registry(registry)
    if any(item.get("case_id") == candidate["case_id"] for item in records):
        print(json.dumps({"status": "blocked", "errors": ["duplicate case_id; create a versioned case instead of overwriting"]}, ensure_ascii=False, indent=2))
        return 1
    supersedes = candidate.get("supersedes")
    if supersedes:
        previous = next((item for item in records if item.get("case_id") == supersedes), None)
        if previous is None:
            print(json.dumps({"status": "blocked", "errors": ["supersedes must reference an existing case_id"]}, ensure_ascii=False, indent=2))
            return 1
        if previous.get("classification") != candidate.get("classification"):
            print(json.dumps({"status": "blocked", "errors": ["superseding records must keep the same I x H classification"]}, ensure_ascii=False, indent=2))
            return 1
        if (previous.get("promotion") or {}).get("status") == "promoted":
            print(json.dumps({"status": "blocked", "errors": ["promoted rules cannot be superseded by a single project case"]}, ensure_ascii=False, indent=2))
            return 1
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")) + "\n")
    confidence = "stable" if candidate.get("status") == "accepted" else "advisory"
    print(json.dumps({"status": "recorded", "case_id": candidate["case_id"], "confidence": confidence, "registry": str(registry)}, ensure_ascii=False))
    return 0


def validate_file(args) -> int:
    candidate = json.loads(Path(args.file).read_text(encoding="utf-8"))
    errors = validate(candidate)
    print(json.dumps({"status": "passed" if not errors else "blocked", "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Query and safely extend the Dayan PPT learning registry.")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--industry")
    query_parser.add_argument("--scenario")
    query_parser.add_argument("--stable-only", action="store_true")
    query_parser.add_argument("--include-rejected", action="store_true")
    query_parser.add_argument("--include-candidates", action="store_true", help=argparse.SUPPRESS)
    query_parser.add_argument("--limit", type=int, default=8, choices=range(1, 51))
    query_parser.set_defaults(func=query)

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("--file", required=True)
    record_parser.set_defaults(func=record)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--file", required=True)
    validate_parser.set_defaults(func=validate_file)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
