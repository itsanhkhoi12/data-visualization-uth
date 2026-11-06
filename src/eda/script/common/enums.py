from __future__ import annotations

from enum import Enum


class DatasetSplit(str, Enum):
    TRAIN = "train"
    PUBLIC_TEST = "public_test"


class Status(str, Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT APPLICABLE"
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    CANDIDATE = "CANDIDATE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SourceType(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    SQLITE = "sqlite"
    JSONL = "jsonl"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"


class EvidenceStatus(str, Enum):
    FILESYSTEM_VERIFIED = "FILESYSTEM VERIFIED"
    SOURCE_VERIFIED = "SOURCE VERIFIED"
    DATA_VERIFIED = "DATA VERIFIED"
    SCHEMA_VERIFIED = "SCHEMA VERIFIED"
    RULEBOOK_VERIFIED = "RULEBOOK VERIFIED"
    DOCUMENTED = "DOCUMENTED"
    INFERRED = "INFERRED"
    PROPOSED = "PROPOSED"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT APPLICABLE"


class SemanticType(str, Enum):
    IDENTIFIER = "identifier"
    MEASURE = "measure"
    QUANTITY = "quantity"
    AMOUNT = "amount"
    DATE = "date"
    DATETIME = "datetime"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    TEXT = "text"
    UNKNOWN = "unknown"


class RelationStatus(str, Enum):
    APPROVED = "APPROVED"
    CANDIDATE = "CANDIDATE"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class ChartType(str, Enum):
    BAR = "bar"
    HORIZONTAL_BAR = "horizontal_bar"
    STACKED_BAR = "stacked_bar"
    GROUPED_BAR = "grouped_bar"
    HISTOGRAM = "histogram"
    ECDF = "ecdf"
    BOXPLOT = "boxplot"
    VIOLIN = "violin"
    SCATTER = "scatter"
    HEXBIN = "hexbin"
    HEATMAP = "heatmap"
    LINE = "line"
    DOT = "dot"
    TIMELINE = "timeline"


class ColumnType(str, Enum):
    TEXT = "text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    CATEGORY = "category"
    UNKNOWN = "unknown"


class TableAlignment(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
