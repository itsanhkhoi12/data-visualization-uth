from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from common.enums import Status
from validation.validation_contracts import ValidationLedger

HANDOVER_VERSION = "handover_report.v1"


@dataclass
class HandoverSection:
    title: str
    lines: list[str] = field(default_factory=list)
    table: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "lines": list(self.lines),
            "table": list(self.table),
        }


@dataclass
class HandoverReport:
    run_id: str
    output_root: Path
    sections: list[HandoverSection] = field(default_factory=list)

    def add(self, section: HandoverSection) -> None:
        self.sections.append(section)

    def to_dict(self) -> dict[str, Any]:
        return {
            "handover_version": HANDOVER_VERSION,
            "run_id": self.run_id,
            "output_root": str(self.output_root),
            "section_count": len(self.sections),
            "sections": [section.to_dict() for section in self.sections],
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Bàn giao kết quả EDA khoa học — run `{self.run_id}`",
            "",
        ]
        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            for item in section.lines:
                lines.append(f"- {item}")
            if section.table:
                headers = list(section.table[0])
                lines.append("")
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join("---" for _ in headers) + " |")
                for row in section.table:
                    lines.append(
                        "| "
                        + " | ".join(str(row.get(header, "")) for header in headers)
                        + " |"
                    )
            lines.append("")
        return "\n".join(lines)


def audit_final_report(
    run: Any,
    validation_ledger: ValidationLedger | None = None,
) -> HandoverReport:
    report = HandoverReport(
        run_id=run.run_id,
        output_root=run.output_root,
    )
    report.add(_coverage_section(run))
    report.add(_quality_section(run, validation_ledger))
    report.add(_narrative_section(run))
    report.add(_provenance_section(run))
    report.add(_limitations_section(run))
    report.add(_deliverables_section(run))
    return report


def produce_handover(
    run: Any,
    validation_ledger: ValidationLedger | None = None,
    target: Path | None = None,
) -> tuple[HandoverReport, Path]:
    report = audit_final_report(run, validation_ledger)
    destination = target or (run.output_root / "reports" / "handover_report.md")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report.to_markdown(), encoding="utf-8")
    payload_path = destination.with_suffix(".json")
    payload_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report, destination


def _coverage_section(run: Any) -> HandoverSection:
    section = HandoverSection(title="1. Phạm vi phân tích và mức độ bao phủ")
    figures = run.visualization.registry.figures if run.visualization else []
    statuses: dict[str, int] = {}
    for record in figures:
        statuses[record.status.value] = statuses.get(record.status.value, 0) + 1
    section.lines.append(
        f"Run ID: `{run.run_id}`; output root: `{run.output_root}`."
    )
    section.lines.append(
        "Các split được phân tích: "
        + ", ".join(f"`{split}`" for split in sorted(run.bundles))
        + "."
    )
    for split in sorted(run.bundles):
        bundle = run.bundles[split]
        section.lines.append(
            f"Split `{split}`: {len(bundle.manifest.records)} tệp nguồn, "
            f"{len(bundle.business_profiles)} doanh nghiệp, "
            f"{len(bundle.column_entries)} cột đã kiểm tra, "
            f"{len(bundle.findings)} phát hiện chất lượng."
        )
    section.lines.append(
        f"Tổng số hình dựng: {len(figures)} với trạng thái {statuses}; "
        f"số nhóm biểu đồ có ít nhất một hình: "
        f"{len({record.chart_id for record in figures})}."
    )
    section.table = [
        {"chỉ số": "tệp nguồn", "giá trị": sum(
            len(bundle.manifest.records) for bundle in run.bundles.values()
        )},
        {"chỉ số": "doanh nghiệp", "giá trị": sum(
            len(bundle.business_profiles) for bundle in run.bundles.values()
        )},
        {"chỉ số": "cột đã kiểm tra", "giá trị": sum(
            len(bundle.column_entries) for bundle in run.bundles.values()
        )},
        {"chỉ số": "phát hiện chất lượng", "giá trị": sum(
            len(bundle.findings) for bundle in run.bundles.values()
        )},
        {"chỉ số": "hình dựng", "giá trị": len(figures)},
        {"chỉ số": "thẻ chuyện khoa học", "giá trị": len(run.story_cards)},
        {"chỉ số": "phát hiện có bằng chứng", "giá trị": len(run.evidence_findings)},
    ]
    return section


def _quality_section(
    run: Any, validation_ledger: ValidationLedger | None
) -> HandoverSection:
    section = HandoverSection(title="2. Kiểm định chất lượng và tính tái lập")
    counts: dict[str, int] = {}
    for gate in run.gates:
        counts[gate.status.value] = counts.get(gate.status.value, 0) + 1
    section.lines.append(
        f"Ledger kiểm định: {len(run.gates)} gate với trạng thái {counts}."
    )
    if validation_ledger is not None:
        qa_counts = validation_ledger.counts()
        failures = validation_ledger.failures()
        section.lines.append(
            f"Kiểm tra QA tự động: {len(validation_ledger.checks)} kiểm tra, "
            f"trạng thái {qa_counts}."
        )
        if failures:
            section.lines.append(
                "Các kiểm tra chưa đạt: "
                + ", ".join(item.check_id for item in failures[:10])
                + "."
            )
        else:
            section.lines.append("Không có kiểm tra QA nào chưa đạt.")
    section.table = [
        {"gate": gate.phase, "tên": gate.gate, "trạng thái": gate.status.value,
         "bằng chứng": gate.artifact or gate.reason[:80]}
        for gate in run.gates
    ]
    return section


def _narrative_section(run: Any) -> HandoverSection:
    section = HandoverSection(title="3. Kể chuyện khoa học và bằng chứng")
    section.lines.append(
        f"{len(run.story_cards)} thẻ chuyện khoa học 9 bước được sinh tự động từ "
        "metric registry đã kiểm chứng."
    )
    section.lines.append(
        f"{len(run.evidence_findings)} phát hiện có bằng chứng gắn source hash, "
        "phương pháp và giới hạn."
    )
    if run.global_report is not None:
        payload = run.global_report.to_dict()
        conclusions = payload.get("scientific_conclusions", [])
        section.lines.append(
            f"{len(conclusions)} kết luận khoa học trong global report, mỗi kết luận "
            "có mức tin cậy và đường dẫn bằng chứng."
        )
        section.table = [
            {
                "mã": item.get("finding_id", ""),
                "phát biểu": item.get("claim", "")[:160],
                "mức tin cậy": item.get("confidence", ""),
            }
            for item in conclusions
        ]
    return section


def _provenance_section(run: Any) -> HandoverSection:
    section = HandoverSection(title="4. Dòng dẫn và khả năng tái lập")
    section.lines.append(
        "Mọi artifact đều được ghi trong `artifact_registry.json` kèm hash nội dung, "
        "nguồn, phương pháp, quy tắc và gate kiểm định."
    )
    section.lines.append(
        "Nguồn thao chỉnh chỉ được đọc; hash của từng tệp thô được kiểm tra lại sau "
        "mỗi run và ghi vào `reports/validation_ledger.json`."
    )
    manifest = run.output_root / "run_manifest.json"
    if manifest.exists():
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        section.lines.append(
            f"Config hash: `{payload.get('config_hash', '')}`; "
            f"rule hash: `{payload.get('rule_hash', '')}`."
        )
        section.lines.append(
            f"Số nguồn được hash: {payload.get('source_hash_count', 0)}; "
            f"chế độ chỉ đọc: {payload.get('read_only', True)}."
        )
    return section


def _limitations_section(run: Any) -> HandoverSection:
    section = HandoverSection(title="5. Hạn chế đã biết")
    limitations: list[str] = []
    if run.global_report is not None:
        payload = run.global_report.to_dict()
        limitations.extend(payload.get("science_limitations", []))
    if not limitations:
        limitations.append(
            "Chưa đủ bằng chứng để đánh giá hạn chế; mọi phát biểu chỉ mô tả số liệu "
            "quan sát."
        )
    section.lines.extend(limitations)
    return section


def _deliverables_section(run: Any) -> HandoverSection:
    section = HandoverSection(title="6. Sản phẩm bàn giao")
    deliverables = [
        ("figure_registry.json", "registry hình dựng kèm trạng thái và hash"),
        ("chart_registry.json", "registry đặc tả biểu đồ đã kiểm chứng"),
        ("table_registry.json", "registry đặc tả bảng HTML"),
        ("gate_ledger.json", "ledger trạng thái theo phase kiểm định"),
        ("artifact_registry.json", "registry artifact có checksum và dòng dẫn"),
        ("reports/evidence_findings.json", "phát hiện tiếng Việt có bằng chứng"),
        ("reports/story_cards.json", "thẻ chuyện khoa học 9 bước"),
        ("reports/validation_ledger.json", "ledger kiểm tra QA tự động"),
        ("reports/global_report.json", "báo cáo khoa học toàn cục"),
        ("src/eda/notebook/eda.ipynb", "notebook trình bày 17 phần"),
    ]
    for name, description in deliverables:
        target = run.output_root / name
        if name.startswith("src/"):
            exists = (
                run.config.workspace_root / name
            ).exists()
        else:
            exists = target.exists()
        section.lines.append(
            f"`{name}` — {description} — "
            + ("đã tạo" if exists else "chưa tạo")
            + "."
        )
    section.table = [
        {"artifact": name, "mô tả": description}
        for name, description in deliverables
    ]
    return section
