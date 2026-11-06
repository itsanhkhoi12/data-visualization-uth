from __future__ import annotations


class EdaError(Exception):
    code = "EDA_ERROR"


class SourceMissing(EdaError):
    code = "SOURCE_MISSING"


class InvalidSchema(EdaError):
    code = "INVALID_SCHEMA"


class UnverifiedJoin(EdaError):
    code = "UNVERIFIED_JOIN"


class UnsupportedBusinessMetric(EdaError):
    code = "UNSUPPORTED_BUSINESS_METRIC"


class RulebookConflict(EdaError):
    code = "RULEBOOK_CONFLICT"


class ResourceBudgetExceeded(EdaError):
    code = "RESOURCE_BUDGET_EXCEEDED"


class UnsafeOutputPath(EdaError):
    code = "UNSAFE_OUTPUT_PATH"


class SourceReadError(EdaError):
    code = "SOURCE_READ_ERROR"


class LabelLeakageError(EdaError):
    code = "LABEL_LEAKAGE"


class CorruptArchiveError(EdaError):
    code = "CORRUPT_ARCHIVE"
