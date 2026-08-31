#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("learning_registry.py")
SKILL_FILE = Path(__file__).resolve().parent.parent / "SKILL.md"


def make_record(case_id, status="candidate", supersedes=None):
    record = {
        "case_id": case_id,
        "date": "2026-07-29",
        "status": status,
        "classification": {
            "industry_code": "I01",
            "scenario_code": "H03",
        },
        "stage": "planning",
        "audience_type": "决策与评审人员",
        "input_types": ["multi-sheet-xlsx"],
        "accepted_patterns": ["先呈现结论再展开证据", "先呈现结论再展开证据"],
        "rejected_patterns": ["把内部判断直接写到页面"],
        "stable_rules": ["读取全部工作表"],
        "style_variables": ["主题色按项目变化"],
        "data_rules": ["所有关键数字必须回到源材料"],
        "qa": {
            "total_score": 90,
            "delivery_complete": True,
            "overflow_free": True,
            "archive_valid": True,
            "hard_failures": [],
            "user_accepted": status == "accepted",
        },
        "promotion": {
            "status": "candidate",
            "supporting_case_ids": [],
            "human_confirmed": False,
        },
        "privacy": {
            "contains_client_data": False,
            "anonymized": True,
        },
    }
    if supersedes:
        record["supersedes"] = supersedes
    return record


class LearningRegistryTests(unittest.TestCase):
    def run_cli(self, registry, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--registry", str(registry), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_record(self, directory, record, name="record.json"):
        path = directory / name
        path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        return path

    def test_delivery_candidate_is_recorded_and_returned_as_advisory(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            registry = directory / "cases.jsonl"
            record_file = self.write_record(directory, make_record("i01-h03-auto-20260729"))

            recorded = self.run_cli(registry, "record", "--file", str(record_file))
            self.assertEqual(recorded.returncode, 0, recorded.stdout + recorded.stderr)

            queried = self.run_cli(registry, "query", "--industry", "I01", "--scenario", "H03")
            self.assertEqual(queried.returncode, 0, queried.stdout + queried.stderr)
            payload = json.loads(queried.stdout)
            self.assertEqual(payload["matches"], 1)
            self.assertEqual(payload["records"][0]["confidence"], "advisory")
            self.assertEqual(payload["guidance"]["advisory_patterns"], ["先呈现结论再展开证据", "读取全部工作表"])

            stored = json.loads(registry.read_text(encoding="utf-8").strip())
            self.assertEqual(stored["accepted_patterns"], ["先呈现结论再展开证据"])

    def test_accepted_case_is_returned_as_stable_guidance(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            registry = directory / "cases.jsonl"
            record_file = self.write_record(directory, make_record("i01-h03-accepted-20260729", status="accepted"))

            recorded = self.run_cli(registry, "record", "--file", str(record_file))
            self.assertEqual(recorded.returncode, 0, recorded.stdout + recorded.stderr)
            queried = self.run_cli(registry, "query", "--industry", "I01", "--scenario", "H03", "--stable-only")
            payload = json.loads(queried.stdout)

            self.assertEqual(payload["matches"], 1)
            self.assertEqual(payload["records"][0]["confidence"], "stable")
            self.assertEqual(payload["guidance"]["stable_patterns"], ["先呈现结论再展开证据"])
            self.assertEqual(payload["guidance"]["stable_rules"], ["读取全部工作表"])

    def test_superseded_candidate_is_hidden_from_future_queries(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            registry = directory / "cases.jsonl"
            first = self.write_record(directory, make_record("i01-h03-version-1-20260729"), "first.json")
            second_record = make_record("i01-h03-version-2-20260729", supersedes="i01-h03-version-1-20260729")
            second_record["rejected_patterns"] = ["旧版结构造成重复反馈"]
            second = self.write_record(directory, second_record, "second.json")

            self.assertEqual(self.run_cli(registry, "record", "--file", str(first)).returncode, 0)
            self.assertEqual(self.run_cli(registry, "record", "--file", str(second)).returncode, 0)
            queried = self.run_cli(registry, "query", "--industry", "I01", "--scenario", "H03")
            payload = json.loads(queried.stdout)

            self.assertEqual(payload["matches"], 1)
            self.assertEqual(payload["records"][0]["case_id"], "i01-h03-version-2-20260729")
            self.assertEqual(payload["guidance"]["avoid_patterns"], ["旧版结构造成重复反馈"])

    def test_stable_records_sort_before_newer_advisory_records(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            registry = directory / "cases.jsonl"
            accepted_record = make_record("i01-h03-stable-order-20260728", status="accepted")
            accepted_record["date"] = "2026-07-28"
            accepted = self.write_record(directory, accepted_record, "accepted.json")
            candidate = self.write_record(directory, make_record("i01-h03-advisory-order-20260729"), "candidate.json")

            self.assertEqual(self.run_cli(registry, "record", "--file", str(accepted)).returncode, 0)
            self.assertEqual(self.run_cli(registry, "record", "--file", str(candidate)).returncode, 0)
            queried = self.run_cli(registry, "query", "--industry", "I01", "--scenario", "H03")
            payload = json.loads(queried.stdout)

            self.assertEqual(payload["records"][0]["case_id"], "i01-h03-stable-order-20260728")
            self.assertEqual(payload["records"][0]["confidence"], "stable")

    def test_candidate_without_delivery_qa_is_blocked(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            registry = directory / "cases.jsonl"
            record = make_record("i01-h03-incomplete-20260729")
            record["qa"]["delivery_complete"] = False
            record_file = self.write_record(directory, record)

            result = self.run_cli(registry, "record", "--file", str(record_file))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate requires qa.delivery_complete=true", result.stdout)

    def test_skill_contract_requires_automatic_candidate_capture_without_silence_promotion(self):
        content = SKILL_FILE.read_text(encoding="utf-8")
        self.assertIn("每次最终交付都必须自动写入候选经验", content)
        self.assertIn("沉默不是验收信号", content)


if __name__ == "__main__":
    unittest.main()
