from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_PATTERN = re.compile(r"^[-*]\s+(.*)$")
TABLE_ROW_PATTERN = re.compile(r"^\|(.*)\|\s*$")
SEPARATOR_ROW_PATTERN = re.compile(r"^[\s:\-|]+$")
HEADER_LABEL_PATTERN = re.compile(
    r"^(luật|cách nói|mặc định|nghĩa|rule|description|default|meaning)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DocumentBlock:
    block_index: int
    kind: str
    heading_level: int
    heading_text: str
    body: tuple[str, ...]
    start_line: int
    end_line: int
    table_rows: tuple[tuple[str, ...], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "block_index": self.block_index,
            "kind": self.kind,
            "heading_level": self.heading_level,
            "heading_text": self.heading_text,
            "body": list(self.body),
            "start_line": self.start_line,
            "end_line": self.end_line,
            "table_rows": [list(row) for row in self.table_rows],
        }


@dataclass(frozen=True)
class MarkdownDocument:
    path: Path
    title: str
    blocks: tuple[DocumentBlock, ...]
    line_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "title": self.title,
            "blocks": [block.to_dict() for block in self.blocks],
            "line_count": self.line_count,
        }

    def block_by_heading(self, heading: str) -> DocumentBlock | None:
        for block in self.blocks:
            if block.heading_text.strip().lower() == heading.strip().lower():
                return block
        return None


def _is_separator_row(cells: tuple[str, ...]) -> bool:
    return all(SEPARATOR_ROW_PATTERN.match(cell) for cell in cells if cell)


def _is_header_row(
    cells: tuple[str, ...], lines: list[str], line_index: int
) -> bool:
    if not cells:
        return False
    first = cells[0]
    if HEADER_LABEL_PATTERN.match(first):
        return True
    following = lines[line_index] if line_index < len(lines) else ""
    if not following.strip().startswith("|"):
        return False
    following_cells = tuple(
        cell.strip() for cell in following.strip().strip("|").split("|")
    )
    return _is_separator_row(following_cells)


def parse_markdown(path: Path) -> MarkdownDocument:
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: list[DocumentBlock] = []
    current_heading = ""
    current_level = 0
    body: list[str] = []
    table_rows: list[tuple[str, ...]] = []
    start_line = 1

    def flush(end_line: int) -> None:
        if not current_heading and not body and not table_rows:
            return
        blocks.append(
            DocumentBlock(
                block_index=len(blocks),
                kind="section" if current_heading else "preamble",
                heading_level=current_level,
                heading_text=current_heading,
                body=tuple(body),
                start_line=start_line,
                end_line=end_line,
                table_rows=tuple(table_rows),
            )
        )

    for index, line in enumerate(lines, start=1):
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            flush(index - 1)
            current_level = len(heading_match.group(1))
            current_heading = heading_match.group(2).strip()
            body = []
            table_rows = []
            start_line = index
            continue
        table_match = TABLE_ROW_PATTERN.match(line)
        if table_match:
            cells = tuple(cell.strip() for cell in table_match.group(1).split("|"))
            if not any(cell for cell in cells):
                continue
            if _is_separator_row(cells):
                continue
            if _is_header_row(cells, lines, index):
                continue
            table_rows.append(cells)
            continue
        body.append(line)
    flush(len(lines))
    title = blocks[0].heading_text if blocks and blocks[0].heading_text else path.stem
    return MarkdownDocument(path=path, title=title, blocks=tuple(blocks), line_count=len(lines))


def read_business_readme(path: Path) -> MarkdownDocument:
    return parse_markdown(path)


def read_rulebook(path: Path) -> MarkdownDocument:
    return parse_markdown(path)


def extract_table_rules(document: MarkdownDocument) -> list[tuple[str, str, str, int]]:
    rules: list[tuple[str, str, str, int]] = []
    for block in document.blocks:
        for row in block.table_rows:
            if len(row) < 2:
                continue
            if row[0].lower() in {"luật", "cách nói"}:
                continue
            rules.append((block.heading_text, row[0], row[1], block.start_line))
    return rules


def extract_bullets(document: MarkdownDocument) -> list[tuple[str, str, int]]:
    items: list[tuple[str, str, int]] = []
    for block in document.blocks:
        for line in block.body:
            match = BULLET_PATTERN.match(line.strip())
            if match:
                items.append((block.heading_text, match.group(1).strip(), block.start_line))
    return items
