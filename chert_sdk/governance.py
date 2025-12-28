"""
Governance manager for governance operations and proposals.
"""

from typing import List, Dict

from .client import ChertClient
from .exceptions import GovernanceError, ValidationError
from .types import Proposal, VoteTally, VoteOption, VoteRequest


class GovernanceManager:
    """Handles governance operations and proposals."""

    def __init__(self, client: ChertClient):
        self.client = client

    async def get_proposals(self, limit: int = 10) -> List[Proposal]:
        """Get the list of governance proposals."""
        params = {}
        if limit > 0:
            params["limit"] = limit
        return await self.client._rpc_call("governance_getProposals", [params], List[Proposal])

    async def get_proposal(self, proposal_id: str) -> Proposal:
        """Get a specific proposal by ID."""
        if not proposal_id:
            raise ValidationError("proposal_id", "Proposal ID cannot be empty")
        return await self.client._rpc_call("governance_getProposal", [proposal_id], Proposal)

    async def create_proposal(self, title: str, description: str, proposer_address: str, fee: str) -> str:
        """Create a new governance proposal."""
        if not title or not description:
            raise ValidationError("proposal", "Title and description are required")

        params = {
            "title": title,
            "description": description,
            "proposer": proposer_address,
            "fee": fee,
        }
        result = await self.client._rpc_call("governance_createProposal", [params])
        if isinstance(result, dict) and "proposal_id" in result:
            return result["proposal_id"]
        raise GovernanceError("Invalid proposal creation response")

    async def vote(self, proposal_id: str, voter_address: str, option: VoteOption, fee: str) -> str:
        """Cast a vote on a governance proposal."""
        request = VoteRequest(
            proposal_id=proposal_id,
            option=option,
            fee=fee
        )
        result = await self.client._rpc_call("governance_vote", [request.dict()])
        if isinstance(result, dict) and "tx_hash" in result:
            return result["tx_hash"]
        raise GovernanceError("Invalid vote response")

    async def get_proposal_votes(self, proposal_id: str) -> VoteTally:
        """Get votes for a specific proposal."""
        return await self.client._rpc_call("governance_getProposalVotes", [proposal_id], VoteTally)

    async def get_voter_votes(self, voter_address: str) -> Dict[str, VoteOption]:
        """Get votes cast by a specific voter."""
        return await self.client._rpc_call("governance_getVoterVotes", [voter_address])

    async def execute_proposal(self, proposal_id: str, executor_address: str, fee: str) -> str:
        """Execute a passed proposal."""
        params = {
            "proposal_id": proposal_id,
            "executor": executor_address,
            "fee": fee,
        }
        result = await self.client._rpc_call("governance_executeProposal", [params])
        if isinstance(result, dict) and "tx_hash" in result:
            return result["tx_hash"]
        raise GovernanceError("Invalid proposal execution response")