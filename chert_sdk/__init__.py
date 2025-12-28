"""
Chert SDK for Python - Official SDK for the Chert/Silica blockchain network.

This SDK provides a comprehensive interface for interacting with the Chert blockchain,
including wallet management, privacy features, staking, and governance operations.

Example:
    >>> from chert_sdk import ChertClient
    >>>
    >>> client = ChertClient()
    >>> account = await client.wallet.create_account()
    >>> print(f"Created account: {account.address}")
"""

from .client import ChertClient
from .types import *
from .exceptions import *

__version__ = "0.1.0"
__all__ = [
    "ChertClient",
    # Networks
    "Network",
    # Account types
    "Account",
    "Balance",
    # Transaction types
    "TransactionRequest",
    "Transaction",
    "TransactionStatus",
    # Privacy types
    "StealthKeys",
    "KeyPair",
    "StealthAccount",
    "PrivacyLevel",
    "PrivateTransactionRequest",
    "PrivateTransaction",
    # Staking types
    "Validator",
    "ValidatorStatus",
    "DelegationRequest",
    "Delegation",
    "StakingRewards",
    # Governance types
    "Proposal",
    "ProposalStatus",
    "VoteTally",
    "VoteOption",
    "VoteRequest",
    # Network types
    "NetworkStatus",
    "Block",
    "Fee",
    # API types
    "APIResponse",
    "JSONRPCRequest",
    "JSONRPCResponse",
    # Exceptions
    "ChertError",
    "NetworkError",
    "APIError",
    "ValidationError",
    "TransactionError",
    "WalletError",
    "PrivacyError",
    "StakingError",
    "GovernanceError",
    "ConfigurationError",
    "CryptoError",
    "TimeoutError",
]