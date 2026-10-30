#!/usr/bin/env python3
"""Focused tests for the DSH evidence-narrative checker."""

from __future__ import annotations

import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import dsh_narrative_check as checker  # noqa: E402


GOOD_SPEC = """# Demo - Design Spec

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Visual style**: swiss-minimal
- **Narrative spine**: dsh-evidence-arc

## IX. Content Outline

#### Slide 01 - Cover

- **Beat**: hook
- **Title**: 校园活动，自动抵达
- **Core message**: 22 天里，它替你试了 547 次。
- **Source**: logs/抢活动.log，2026-10-08 至 2026-10-30

#### Slide 02 - Why

- **Beat**: conflict
- **Relationships**: contrast between 手动 30 秒 and 名额几秒
- **Title**: 名额不等人
- **Content**: 手动一遍 30 秒，名额几秒就没了。
- **Data class**: scenario — 量级估计，未实测

#### Slide 03 - How

- **Beat**: method
- **Relationships**: order 01→04
- **Title**: 四道工序
- **Mapping**: 对时 → 时钟误差；巡检 → 盯屏；并行 → 多活动；重试 → 空等
- **Source**: 源码 http.py，2026-10

#### Slide 04 - Result

- **Beat**: evidence
- **Relationships**: order 统计 → 边界
- **Title**: 22 天，它替你跑了这些
- **Content**: 547 次成功登录；545 轮巡检；30 次报名；74,226 行日志。
- **Fact IDs**: F001, F002, F003, F004
- **Boundary**: 其余尝试多数卡在接口连接超时，不是抢失败；30 次不是「全中」，是能进的窗口里一次没漏。
"""

GOOD_NARRATIVE = """# Narrative Spine

- **Spine**: dsh-evidence-arc

## Slide 01 — hook

- **Beat**: hook
- **Title**: 校园活动，自动抵达
- **Claim**: 22 天里，它替你试了 547 次。
- **Source**: logs/抢活动.log，2026-10-08 至 2026-10-30

## Slide 02 — conflict

- **Beat**: conflict
- **Title**: 名额不等人
- **Relationships**: contrast between 手动 30 秒 and 名额几秒
- **Claim**: 手动 30 秒，名额几秒；人不可能 24 小时盯屏。
- **Data class**: scenario — 量级估计

## Slide 03 — method

- **Beat**: method
- **Title**: 四道工序
- **Mapping**: 对时 → 时钟误差；巡检 → 盯屏；并行 → 多活动；重试 → 空等
- **Source**: 源码 http.py，2026-10

## Slide 04 — evidence

- **Beat**: evidence
- **Title**: 22 天，它替你跑了这些
- **Claim**: 547 次登录、545 轮巡检、30 次报名确认、74,226 行日志。
- **Fact IDs**: F001, F002, F003, F004
- **Boundary**: 失败多为接口超时，不是抢不到；30 次不是「全中」，是能进的窗口里一次没漏。
"""


def _target() -> Path:
    return Path("design_spec.md")


def _codes(text: str, *, require_spine: bool = False) -> set[str]:
    report = checker.check_text(text, target=_target(), require_spine=require_spine)
    return {finding.code for finding in report.findings}


class ApplicabilityTests(unittest.TestCase):
    def test_good_spec_passes(self) -> None:
        report = checker.check_text(GOOD_SPEC, target=_target())
        self.assertTrue(report.ok, report.findings)
        self.assertTrue(report.applicable)
        self.assertEqual(report.spine, checker.SPINE_ID)
        self.assertEqual(report.beats, list(checker.BEAT_ORDER))

    def test_good_quick_narrative_passes(self) -> None:
        report = checker.check_text(GOOD_NARRATIVE, target=Path("narrative.md"))
        self.assertTrue(report.ok, report.findings)
        self.assertEqual(report.slide_count, 4)

    def test_missing_spine_is_not_applicable_without_require(self) -> None:
        report = checker.check_text("# Notes\n\nNo spine here.\n", target=_target())
        self.assertTrue(report.ok)
        self.assertFalse(report.applicable)

    def test_missing_spine_fails_with_require(self) -> None:
        report = checker.check_text("# Notes\n\nNo spine here.\n", target=_target(), require_spine=True)
        self.assertFalse(report.ok)
        self.assertEqual([finding.code for finding in report.findings], ["SPINE_MISSING"])

    def test_explicit_off_is_allowed(self) -> None:
        text = GOOD_SPEC.replace("- **Narrative spine**: dsh-evidence-arc", "- **Narrative spine**: off — 用户要的是状态汇报")
        report = checker.check_text(text, target=_target(), require_spine=True)
        self.assertTrue(report.ok)
        self.assertFalse(report.applicable)

    def test_unknown_spine_fails(self) -> None:
        text = GOOD_SPEC.replace("- **Narrative spine**: dsh-evidence-arc", "- **Narrative spine**: pyramid")
        self.assertIn("SPINE_UNKNOWN", _codes(text))


class BeatContractTests(unittest.TestCase):
    def test_missing_conflict_beat(self) -> None:
        text = GOOD_SPEC.replace("- **Beat**: conflict", "- **Beat**: method")
        self.assertIn("BEAT_MISSING", _codes(text))

    def test_duplicate_beat(self) -> None:
        text = GOOD_SPEC.replace("- **Beat**: conflict", "- **Beat**: hook")
        self.assertIn("BEAT_DUPLICATE", _codes(text))

    def test_out_of_order_beats(self) -> None:
        text = (
            GOOD_SPEC.replace("- **Beat**: hook", "- **Beat**: pending")
            .replace("- **Beat**: conflict", "- **Beat**: hook")
            .replace("- **Beat**: pending", "- **Beat**: conflict")
        )
        self.assertIn("BEAT_ORDER", _codes(text))

    def test_hook_without_number(self) -> None:
        text = GOOD_SPEC.replace("22 天里，它替你试了 547 次。", "它一直替你盯着。")
        self.assertIn("HOOK_NO_NUMBER", _codes(text))

    def test_conflict_without_contrast(self) -> None:
        text = GOOD_SPEC.replace(
            "- **Relationships**: contrast between 手动 30 秒 and 名额几秒",
            "- **Relationships**: 两件互不相干的事",
        )
        self.assertIn("CONFLICT_NO_CONTRAST", _codes(text))

    def test_method_without_mapping(self) -> None:
        text = GOOD_SPEC.replace(
            "- **Mapping**: 对时 → 时钟误差；巡检 → 盯屏；并行 → 多活动；重试 → 空等",
            "- **Mapping**: 对时 → 时钟误差",
        )
        self.assertIn("METHOD_NO_MAPPING", _codes(text))

    def test_evidence_without_boundary(self) -> None:
        text = GOOD_SPEC.replace(
            "- **Boundary**: 其余尝试多数卡在接口连接超时，不是抢失败；30 次不是「全中」，是能进的窗口里一次没漏。",
            "- **Boundary**: 无",
        )
        self.assertIn("EVIDENCE_NO_BOUNDARY", _codes(text))

    def test_evidence_must_be_last_beat(self) -> None:
        text = GOOD_SPEC.replace(
            "#### Slide 03 - How\n\n- **Beat**: method",
            "#### Slide 03 - How\n\n- **Beat**: evidence",
        ).replace(
            "#### Slide 04 - Result\n\n- **Beat**: evidence",
            "#### Slide 04 - Result\n\n- **Beat**: method",
        )
        codes = _codes(text)
        self.assertIn("EVIDENCE_NOT_LAST", codes)

    def test_unsourced_number_on_beat_page(self) -> None:
        text = GOOD_SPEC.replace(
            "- **Source**: 源码 http.py，2026-10",
            "- **Note**: 没有来源",
        )
        # The mapping page still carries no quantity, so inject one without provenance.
        text = text.replace("- **Title**: 四道工序", "- **Title**: 四道工序，每 30 分钟一轮")
        self.assertIn("NUMBER_UNSOURCED", _codes(text))


class AbsoluteClaimTests(unittest.TestCase):
    def test_bare_absolute_claim_fails(self) -> None:
        text = GOOD_SPEC.replace(
            "- **Core message**: 22 天里，它替你试了 547 次。", "- **Core message**: 百发百中。"
        ).replace("- **Source**: logs/抢活动.log，2026-10-08 至 2026-10-30", "- **Note**: 没有出处")
        self.assertIn("ABSOLUTE_CLAIM", _codes(text))

    def test_negated_absolute_claim_passes(self) -> None:
        text = GOOD_SPEC.replace(
            "- **Core message**: 22 天里，它替你试了 547 次。",
            "- **Core message**: 这不是百发百中，是能进的窗口里一次没漏。",
        )
        self.assertNotIn("ABSOLUTE_CLAIM", _codes(text))


class ResolveTargetTests(unittest.TestCase):
    def test_prefers_design_spec(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "design_spec.md").write_text(GOOD_SPEC, encoding="utf-8")
            (root / "narrative.md").write_text(GOOD_NARRATIVE, encoding="utf-8")
            target, text = checker.resolve_target(root)
            self.assertEqual(target.name, "design_spec.md")
            self.assertIn("Narrative spine", text)

    def test_falls_back_to_narrative(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "design_spec.md").write_text("# Old spec\n", encoding="utf-8")
            (root / "narrative.md").write_text(GOOD_NARRATIVE, encoding="utf-8")
            target, _ = checker.resolve_target(root)
            self.assertEqual(target.name, "narrative.md")

    def test_missing_artifacts_raise(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                checker.resolve_target(Path(directory))


REFERENCE_DOC = Path(__file__).resolve().parents[2] / "references" / "dsh-narrative.md"
EXAMPLE_DOC = Path(__file__).resolve().parents[2] / "examples" / "narrative-evidence-arc.md"


def _markdown_blocks(text: str) -> list[str]:
    return re.findall(r"```markdown\n(.*?)```", text, re.DOTALL)


class DocumentedExampleTests(unittest.TestCase):
    """The syntax examples in the authority doc must pass the checker verbatim."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.blocks = _markdown_blocks(REFERENCE_DOC.read_text(encoding="utf-8"))

    def test_documented_default_example_passes(self) -> None:
        spine = next(block for block in self.blocks if "Narrative spine" in block)
        slides = next(block for block in self.blocks if "#### Slide 01" in block)
        report = checker.check_text(spine + "\n\n" + slides, target=Path("design_spec.md"))
        self.assertTrue(report.ok, report.findings)
        self.assertTrue(report.applicable)

    def test_documented_quick_example_passes(self) -> None:
        quick = next(block for block in self.blocks if "## Slide 01" in block and "Spine" in block)
        report = checker.check_text(quick, target=Path("narrative.md"))
        self.assertTrue(report.ok, report.findings)
        self.assertEqual(report.slide_count, 4)


class RepositoryExampleTests(unittest.TestCase):
    """The shipped narrative example must stay valid against the checker."""

    def test_shipped_example_passes(self) -> None:
        report = checker.check_text(EXAMPLE_DOC.read_text(encoding="utf-8"), target=EXAMPLE_DOC)
        self.assertTrue(report.ok, report.findings)
        self.assertTrue(report.applicable)
        self.assertEqual(report.slide_count, 4)
        self.assertEqual(report.beats, list(checker.BEAT_ORDER))


class CommandTests(unittest.TestCase):
    def test_main_exit_codes_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "narrative.md").write_text(GOOD_NARRATIVE, encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = checker.main([str(root), "--require", "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["applicable"])
            self.assertEqual(payload["beats"], list(checker.BEAT_ORDER))

    def test_require_fails_on_spec_without_spine(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "design_spec.md").write_text("# Spec\n\n## IX. Content Outline\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = checker.main([str(root), "--require"])
            self.assertEqual(exit_code, 1)
            self.assertIn("SPINE_MISSING", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
