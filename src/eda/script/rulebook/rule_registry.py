from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from readers.markdown_reader import MarkdownDocument, extract_table_rules, parse_markdown

SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    split: str
    section: str
    rule_label: str
    rule_text: str
    source_line: int
    status: str = "VERIFIED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "split": self.split,
            "section": self.section,
            "rule_label": self.rule_label,
            "rule_text": self.rule_text,
            "source_line": self.source_line,
            "status": self.status,
        }


@dataclass(frozen=True)
class RuleRegistry:
    split: str
    path: Path
    title: str
    rules: tuple[RuleDefinition, ...]
    sections: tuple[str, ...]
    line_count: int
    rulebook_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "path": str(self.path),
            "title": self.title,
            "rules": [rule.to_dict() for rule in self.rules],
            "sections": list(self.sections),
            "line_count": self.line_count,
            "rulebook_hash": self.rulebook_hash,
        }

    def rule_by_id(self, rule_id: str) -> RuleDefinition | None:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None


def slugify(text: str) -> str:
    return SLUG_PATTERN.sub("_", text.strip().lower()).strip("_")


def compile_rule_registry(path: Path, split: str, rulebook_hash: str) -> RuleRegistry:
    document: MarkdownDocument = parse_markdown(path)
    rules: list[RuleDefinition] = []
    seen_labels: dict[str, int] = {}
    for section, label, text, line in extract_table_rules(document):
        base_slug = slugify(label)
        seen_labels[base_slug] = seen_labels.get(base_slug, 0) + 1
        slug = base_slug if seen_labels[base_slug] == 1 else f"{base_slug}_{seen_labels[base_slug]}"
        rule_id = f"{split}.{slugify(section)}.{slug}"
        rules.append(
            RuleDefinition(
                rule_id=rule_id,
                split=split,
                section=section,
                rule_label=label,
                rule_text=text,
                source_line=line,
            )
        )
    sections = tuple(
        block.heading_text for block in document.blocks if block.heading_level >= 2
    )
    return RuleRegistry(
        split=split,
        path=path,
        title=document.title,
        rules=tuple(rules),
        sections=sections,
        line_count=document.line_count,
        rulebook_hash=rulebook_hash,
    )
