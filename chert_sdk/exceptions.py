"""
Exception classes for the Chert SDK.
"""

from typing import Optional, Dict, Any


class ChertError(Exception):
    """Base exception class for Chert SDK errors."""

    def __init__(self, message: str, code: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.data = data or {}

    def __str__(self) -> str:
        if self.code:
            return f"{self.code}: {self.message}"
        return self.message


class NetworkError(ChertError):
    """Network-related errors (connection, timeout, etc.)."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, "NETWORK_ERROR")
        self.cause = cause


class APIError(ChertError):
    """API response errors."""

    def __init__(self, message: str, code: str, status_code: Optional[int] = None, data: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, data)
        self.status_code = status_code


class ValidationError(ChertError):
    """Input validation errors."""

    def __init__(self, field: str, message: str):
        super().__init__(f"Validation error in {field}: {message}", "VALIDATION_ERROR", {"field": field})
        self.field = field


class TransactionError(ChertError):
    """Transaction-related errors."""

    def __init__(self, message: str, tx_hash: Optional[str] = None):
        super().__init__(message, "TRANSACTION_ERROR", {"tx_hash": tx_hash} if tx_hash else None)
        self.tx_hash = tx_hash


class WalletError(ChertError):
    """Wallet and account errors."""

    def __init__(self, message: str):
        super().__init__(message, "WALLET_ERROR")


class PrivacyError(ChertError):
    """Privacy feature errors."""

    def __init__(self, message: str):
        super().__init__(message, "PRIVACY_ERROR")


class StakingError(ChertError):
    """Staking-related errors."""

    def __init__(self, message: str):
        super().__init__(message, "STAKING_ERROR")


class GovernanceError(ChertError):
    """Governance-related errors."""

    def __init__(self, message: str):
        super().__init__(message, "GOVERNANCE_ERROR")


class ConfigurationError(ChertError):
    """Configuration errors."""

    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class CryptoError(ChertError):
    """Cryptographic operation errors."""

    def __init__(self, message: str):
        super().__init__(message, "CRYPTO_ERROR")


class TimeoutError(ChertError):
    """Timeout errors."""

    def __init__(self, operation: str, timeout_seconds: float):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds}s",
            "TIMEOUT_ERROR",
            {"operation": operation, "timeout_seconds": timeout_seconds}
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds