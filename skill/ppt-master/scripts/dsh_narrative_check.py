#!/usr/bin/env python3
"""
PPT Master - DSH Evidence Narrative Checker

Validate the DSH four-beat evidence narrative (hook -> conflict -> method ->
evidence + boundary) recorded in a project's design_spec.md or narrative.md.

Usage:
    python3 scripts/dsh_narrative_check.py <project_path_or_file> [--require] [--json]

Examples:
    python3 scripts/dsh_narrative_check.py projects/demo
    python3 scripts/dsh_narrative_check.py projects/demo/narrative.md --require --json

Dependencies:
    None (only uses the standard library and local project modules)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from console_encoding import configure_utf8_stdio  # noqa: E402


SPINE_ID = "dsh-evidence-arc"
BEAT_ORDER = ("hook", "conflict", "method", "evidence")
MIN_BOUNDARY_CHARS = 12

_SPINE_RE = re.compile(
    r"^[ \t]*[-*][ \t]+(?:\*\*)?(?:Narrative[ \t]+spine|Spine)(?:\*\*)?[ \t]*:[ \t]*(\S.*?)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
_SLIDE_RE = re.compile(
    r"^#{2,6}[ \t]+Slide[ \t]+0*([0-9]+)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)
_FIELD_RE = re.compile(
    r"^[ \t]*[-*][ \t]+(?:\*\*)?([A-Za-z][A-Za-z0-9 /_-]{0,31}?)(?:\*\*)?[ \t]*:[ \t]*(.*?)[ \t]*$"
)
_QUANTITY_RE = re.compile(
    r"[0-9][0-9,.]*[ \t]*(?:%|次|轮|行|天|小时|分钟|分|秒|个|场|条|人|元|万|千|份|页|倍|名|级)"
    r"|\b[0-9][0-9,.]*[ \t]*(?:%|times?|runs?|rows?|days?|hours?|minutes?|seconds?|users?"
    r"|events?|slides?|pages?|people|records?|requests?|attempts?)\b",
    re.IGNORECASE,
)
_ABSOLUTE_RE = re.compile(r"全中|百发百中|稳赢|必胜|零失败|从未失手|百分百|100[ \t]*%")
_ARROW_RE = re.compile(r"→|->|=>")
_CLAIM_FIELDS = {"title", "core message", "content", "claim", "subtitle"}


@dataclass
class Slide:
    """One parsed Slide block: its number, fields, and non-field narrative text."""

    number: int
    heading: str
    fields: dict[str, str] = field(default_factory=dict)
    extra: str = ""

    def value(self, name: str) -> str:
        return self.fields.get(name, "").strip()

    @property
    def beat(self) -> str:
        return self.value("beat").strip(" *_`#").lower()

    @property
    def claim_text(self) -> str:
        parts = [self.fields[name] for name in _CLAIM_FIELDS if name in self.fields]
        parts.append(self.extra)
        return " ".join(part for part in parts if part)

    @property
    def has_provenance(self) -> bool:
        if self.value("fact ids") or self.value("source"):
            return True
        return "scenario" in self.value("data class").lower()


@dataclass(frozen=True)
class Finding:
    """One violation, addressed to a slide when the fault is page-local."""

    code: str
    slide: int | None
    message: str


@dataclass
class Report:
    """The complete evaluation result for one target file."""

    target: Path
    spine: str | None
    applicable: bool
    beats: list[str]
    slide_count: int
    findings: list[Finding]

    @property
    def ok(self) -> bool:
        return not self.findings


def _parse_slides(text: str) -> list[Slide]:
    """Split every Slide block and read its bullet fields without normalizing text."""
    matches = list(_SLIDE_RE.finditer(text))
    slides: list[Slide] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end]
        slide = Slide(number=int(match.group(1)), heading=match.group(0).strip())
        extra: list[str] = []
        for line in body.splitlines():
            field_match = _FIELD_RE.match(line)
            if field_match:
                name = field_match.group(1).strip().lower()
                slide.fields[name] = field_match.group(2).strip()
            elif line.strip():
                extra.append(line.strip())
        slide.extra = " ".join(extra)
        slides.append(slide)
    return slides


def _normalize_spine(value: str) -> str:
    """Trim trailing punctuation a human may add after the spine id."""
    return value.strip().strip("`*_ ").rstrip("。.;；,，").lower()


def _is_negated(text: str, start: int) -> bool:
    """Return whether an absolute claim at `start` is denied in the same clause."""
    window = text[max(0, start - 14):start]
    return re.search(r"(?:不是|并非|不等于|不代表|不算|不|非|未|没|无)[\s「『\"'“”]{0,4}$", window) is not None


def _mapping_count(value: str) -> int:
    return len(_ARROW_RE.findall(value))


def check_text(text: str, *, target: Path, require_spine: bool = False) -> Report:
    """Evaluate the narrative contract over one document's text."""
    spine_match = _SPINE_RE.search(text)
    spine = _normalize_spine(spine_match.group(1)) if spine_match else None
    slides = _parse_slides(text)
    findings: list[Finding] = []

    if spine is None:
        if require_spine:
            findings.append(Finding(
                "SPINE_MISSING",
                None,
                "persuasion deck requires '- **Narrative spine**: dsh-evidence-arc' (or 'off — <reason>')",
            ))
        return Report(target, None, False, [], len(slides), findings)

    if spine.startswith("off") or spine in {"none", "n/a", "na", "不适用", "关闭"}:
        return Report(target, spine, False, [], len(slides), findings)

    if spine != SPINE_ID:
        findings.append(Finding(
            "SPINE_UNKNOWN",
            None,
            f"spine '{spine}' is not '{SPINE_ID}' and is not an explicit 'off' opt-out",
        ))
        return Report(target, spine, True, [], len(slides), findings)

    beat_slides = [slide for slide in slides if slide.beat]
    for slide in beat_slides:
        if slide.beat not in BEAT_ORDER:
            findings.append(Finding(
                "BEAT_UNKNOWN",
                slide.number,
                f"beat '{slide.beat}' is not one of {', '.join(BEAT_ORDER)}",
            ))

    counts = Counter(slide.beat for slide in beat_slides if slide.beat in BEAT_ORDER)
    for beat in BEAT_ORDER:
        if counts[beat] == 0:
            findings.append(Finding("BEAT_MISSING", None, f"no slide is marked '- **Beat**: {beat}'"))
        elif counts[beat] > 1:
            findings.append(Finding("BEAT_DUPLICATE", None, f"beat '{beat}' appears {counts[beat]} times"))
    if all(counts[beat] == 1 for beat in BEAT_ORDER):
        sequence = [slide.beat for slide in beat_slides if slide.beat in BEAT_ORDER]
        if sequence != list(BEAT_ORDER):
            findings.append(Finding(
                "BEAT_ORDER",
                None,
                f"beats run {' → '.join(sequence)}; the contract is {' → '.join(BEAT_ORDER)}",
            ))

    by_beat = {slide.beat: slide for slide in beat_slides if slide.beat in BEAT_ORDER}
    for slide in beat_slides:
        if _QUANTITY_RE.search(slide.claim_text) and not slide.has_provenance:
            findings.append(Finding(
                "NUMBER_UNSOURCED",
                slide.number,
                "quantified claim has no '- **Fact IDs**', '- **Source**', or 'Data class: scenario'",
            ))
        claim_blob = slide.claim_text
        for absolute in _ABSOLUTE_RE.finditer(claim_blob):
            if _is_negated(claim_blob, absolute.start()) or slide.has_provenance:
                continue
            findings.append(Finding(
                "ABSOLUTE_CLAIM",
                slide.number,
                f"absolute claim '{absolute.group(0)}' has no provenance on this page",
            ))
            break

    hook = by_beat.get("hook")
    if hook is not None and not _QUANTITY_RE.search(hook.claim_text):
        findings.append(Finding(
            "HOOK_NO_NUMBER",
            hook.number,
            "hook page carries no number; the cover must make scale concrete",
        ))

    conflict = by_beat.get("conflict")
    if conflict is not None and "contrast" not in conflict.value("relationships").lower():
        findings.append(Finding(
            "CONFLICT_NO_CONTRAST",
            conflict.number,
            "conflict page Relationships must state a 'contrast' between the two costs",
        ))

    method = by_beat.get("method")
    if method is not None and _mapping_count(method.value("mapping")) < 2:
        findings.append(Finding(
            "METHOD_NO_MAPPING",
            method.number,
            "method page needs a '- **Mapping**:' line with at least two '→' mappings to conflict costs",
        ))

    evidence = by_beat.get("evidence")
    if evidence is not None:
        boundary = evidence.value("boundary")
        if len(boundary) < MIN_BOUNDARY_CHARS:
            findings.append(Finding(
                "EVIDENCE_NO_BOUNDARY",
                evidence.number,
                f"evidence page needs a substantive '- **Boundary**:' line ({MIN_BOUNDARY_CHARS}+ chars)",
            ))
        later = [slide.number for slide in beat_slides if slide.beat in BEAT_ORDER and slide.number > evidence.number]
        if later:
            findings.append(Finding(
                "EVIDENCE_NOT_LAST",
                evidence.number,
                f"beat page(s) {', '.join(str(number) for number in later)} follow the evidence page",
            ))

    beats = [slide.beat for slide in beat_slides if slide.beat in BEAT_ORDER]
    return Report(target, spine, True, beats, len(slides), findings)


def resolve_target(path: Path) -> tuple[Path, str]:
    """Resolve a project directory to its design_spec.md, else its narrative.md."""
    if path.is_file():
        return path, path.read_text(encoding="utf-8")

    if not path.is_dir():
        raise FileNotFoundError(f"{path} is neither a file nor a directory")

    spec = path / "design_spec.md"
    narrative = path / "narrative.md"
    if spec.is_file():
        text = spec.read_text(encoding="utf-8")
        if _SPINE_RE.search(text) or not narrative.is_file():
            return spec, text
    if narrative.is_file():
        return narrative, narrative.read_text(encoding="utf-8")
    raise FileNotFoundError(f"{path} has neither design_spec.md nor narrative.md")


def _print_report(report: Report, *, as_json: bool) -> None:
    payload = {
        "ok": report.ok,
        "applicable": report.applicable,
        "spine": report.spine,
        "target": str(report.target),
        "slides": report.slide_count,
        "beats": report.beats,
        "findings": [
            {"code": item.code, "slide": item.slide, "message": item.message}
            for item in report.findings
        ],
    }
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if report.ok and not report.applicable:
        reason = "opted out" if report.spine else "no spine recorded"
        print(f"DSH narrative check: PASS (not applicable — {reason})")
        return
    if report.ok:
        print(
            "DSH narrative check: PASS "
            f"— {report.spine} | {report.slide_count} slides | {' → '.join(report.beats)}"
        )
        return
    print(f"DSH narrative check: FAIL — {len(report.findings)} finding(s) in {report.target}")
    for item in report.findings:
        where = f"slide {item.slide:02d}: " if item.slide is not None else ""
        print(f"  [{item.code}] {where}{item.message}")


def main(argv: list[str] | None = None) -> int:
    """Run the DSH narrative gate over one project or document."""
    parser = argparse.ArgumentParser(
        description="Validate the DSH evidence narrative (hook/conflict/method/evidence).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="Project directory, design_spec.md, or narrative.md")
    parser.add_argument("--require", action="store_true", help="Fail when no narrative spine is recorded")
    parser.add_argument("--json", action="store_true", help="Print one JSON object instead of text")
    args = parser.parse_args(argv)

    try:
        target, text = resolve_target(Path(args.target))
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report = check_text(text, target=target, require_spine=args.require)
    _print_report(report, as_json=args.json)
    return 0 if report.ok else 1


if __name__ == "__main__":
    configure_utf8_stdio()
    raise SystemExit(main())
