"""
Staking manager for staking and delegation operations.
"""

from typing import List

from .client import ChertClient
from .exceptions import StakingError, ValidationError
from .types import Validator, Delegation, StakingRewards, DelegationRequest


class StakingManager:
    """Handles staking and delegation operations."""

    def __init__(self, client: ChertClient):
        self.client = client

    async def get_validators(self) -> List[Validator]:
        """Get the list of validators."""
        return await self.client._rpc_call("getValidators", result_type=List[Validator])

    async def get_validator(self, address: str) -> Validator:
        """Get a specific validator by address."""
        if not address:
            raise ValidationError("address", "Address cannot be empty")
        return await self.client._rpc_call("getValidator", [address], Validator)

    async def delegate(self, delegator_address: str, validator_address: str, amount: str, fee: str) -> str:
        """Delegate tokens to a validator."""
        request = DelegationRequest(
            validator_address=validator_address,
            amount=amount,
            fee=fee
        )
        result = await self.client._rpc_call("staking_delegate", [request.dict()])
        if isinstance(result, dict) and "tx_hash" in result:
            return result["tx_hash"]
        raise StakingError("Invalid delegation response")

    async def undelegate(self, delegator_address: str, validator_address: str, amount: str, fee: str) -> str:
        """Remove delegation from a validator."""
        params = {
            "delegator": delegator_address,
            "validator": validator_address,
            "amount": amount,
            "fee": fee,
        }
        result = await self.client._rpc_call("staking_undelegate", [params])
        if isinstance(result, dict) and "tx_hash" in result:
            return result["tx_hash"]
        raise StakingError("Invalid undelegation response")

    async def get_delegations(self, delegator_address: str) -> List[Delegation]:
        """Get delegations for an account."""
        return await self.client._rpc_call("getDelegations", [delegator_address], List[Delegation])

    async def get_staking_rewards(self, delegator_address: str) -> StakingRewards:
        """Get staking rewards for an account."""
        return await self.client._rpc_call("getStakingRewards", [delegator_address], StakingRewards)

    async def claim_rewards(self, delegator_address: str, validator_address: str, fee: str) -> str:
        """Claim staking rewards."""
        params = {
            "delegator": delegator_address,
            "validator": validator_address,
            "fee": fee,
        }
        result = await self.client._rpc_call("staking_claimRewards", [params])
        if isinstance(result, dict) and "tx_hash" in result:
            return result["tx_hash"]
        raise StakingError("Invalid claim rewards response")