"""Custom exceptions for the Market Expansion Profitability Analyzer."""


class AnalyzerError(Exception):
    """Base class for all application-specific errors."""


class InvalidInputError(AnalyzerError):
    """Raised when a value is non-numeric, out of range, or otherwise invalid."""


class MissingColumnError(AnalyzerError):
    """Raised when a required CSV column or config key is absent."""


class DataFileError(AnalyzerError):
    """Raised when a data file is missing or unreadable."""


class EmptyDatasetError(AnalyzerError):
    """Raised when the dataset contains no usable city rows."""
