"""
Type definitions for the Chert SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# Network types
class Network(str, Enum):
    """Blockchain network types."""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"


# Account types
class Account(BaseModel):
    """Blockchain account information."""
    address: str
    public_key: str
    private_key: Optional[str] = None


class Balance(BaseModel):
    """Account balance information."""
    available: str
    pending: str
    total: str


# Transaction types
class TransactionRequest(BaseModel):
    """Transaction request data."""
    to: str
    amount: str
    fee: str
    memo: Optional[str] = None
    nonce: Optional[int] = None


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REJECTED = "rejected"


class Transaction(BaseModel):
    """Transaction data."""
    hash: str
    from_address: str = Field(..., alias="from")
    to: str
    amount: str
    fee: str
    memo: Optional[str] = None
    block_height: Optional[int] = None
    status: TransactionStatus
    timestamp: datetime
    nonce: int

    class Config:
        allow_population_by_field_name = True


# Privacy types
class KeyPair(BaseModel):
    """Cryptographic key pair."""
    public: str
    secret: str


class StealthKeys(BaseModel):
    """Stealth address key pairs."""
    view_keypair: KeyPair
    spend_keypair: KeyPair


class StealthAccount(BaseModel):
    """Stealth account information."""
    address: str
    view_key: str
    spend_public_key: str
    keys: Optional[StealthKeys] = None


class PrivacyLevel(str, Enum):
    """Privacy level enumeration."""
    STEALTH = "stealth"
    ENCRYPTED = "encrypted"


class PrivateTransactionRequest(BaseModel):
    """Private transaction request."""
    sender_keys: StealthKeys
    recipient_view_key: str
    amount: str
    fee: str
    privacy_level: PrivacyLevel
    nonce: int
    memo: Optional[str] = None


class PrivateTransaction(BaseModel):
    """Private transaction data."""
    tx_id: str
    amount: str
    memo: Optional[str] = None
    sender: Optional[str] = None
    timestamp: datetime
    fee: str


# Staking types
class ValidatorStatus(str, Enum):
    """Validator status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    JAILED = "jailed"


class Validator(BaseModel):
    """Validator information."""
    address: str
    name: str
    voting_power: str
    commission: str
    status: ValidatorStatus
    total_delegated: str
    delegator_count: int
    public_key: Optional[str] = None
    stake_amount: Optional[int] = None
    commission_rate: Optional[int] = None
    is_active: Optional[bool] = None
    reputation_score: Optional[float] = None
    last_activity: Optional[datetime] = None


class DelegationRequest(BaseModel):
    """Delegation request."""
    validator_address: str
    amount: str
    fee: str


class Delegation(BaseModel):
    """Delegation information."""
    validator_address: str
    amount: str
    rewards: str
    timestamp: datetime


class StakingRewards(BaseModel):
    """Staking rewards information."""
    total: str
    available: str
    pending: str
    last_claim: Optional[datetime] = None


# Governance types
class ProposalStatus(str, Enum):
    """Proposal status enumeration."""
    VOTING = "voting"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class VoteTally(BaseModel):
    """Vote tally information."""
    yes: str
    no: str
    abstain: str
    no_with_veto: str


class Proposal(BaseModel):
    """Governance proposal."""
    id: str
    title: str
    description: str
    proposer: str
    status: ProposalStatus
    voting_start_time: datetime
    voting_end_time: datetime
    tally: VoteTally


class VoteOption(str, Enum):
    """Vote option enumeration."""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"
    NO_WITH_VETO = "no_with_veto"


class VoteRequest(BaseModel):
    """Vote request."""
    proposal_id: str
    option: VoteOption
    fee: str


# Network types
class NetworkStatus(BaseModel):
    """Network status information."""
    block_height: int
    network_id: str
    consensus_version: str
    peer_count: int
    syncing: bool
    latest_block_time: datetime


class Block(BaseModel):
    """Block information."""
    height: int
    hash: str
    previous_hash: str
    timestamp: datetime
    transaction_count: int
    proposer: str
    transactions: Optional[List[Transaction]] = None


# Fee estimation
class Fee(BaseModel):
    """Fee estimation information."""
    amount: str
    gas_limit: Optional[int] = None
    gas_price: Optional[str] = None


# API response types
class APIResponse(BaseModel):
    """Standard API response."""
    data: Any
    success: bool
    error: Optional[Dict[str, Any]] = None


# JSON-RPC types
class JSONRPCRequest(BaseModel):
    """JSON-RPC request."""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Any] = None
    id: Any = 1


class JSONRPCResponse(BaseModel):
    """JSON-RPC response."""
    jsonrpc: str
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Any


# Configuration
class ClientConfig(BaseModel):
    """Client configuration."""
    endpoint: str = "https://api.chert.com"
    network: Network = Network.MAINNET
    timeout: float = 30.0
    api_key: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)

    class Config:
        use_enum_values = True