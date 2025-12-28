"""
Main client implementation for the Chert SDK.
"""

import asyncio
import hashlib
import secrets
from typing import Dict, Optional, Any
from urllib.parse import urljoin

import aiohttp
from pydantic import ValidationError

from .exceptions import (
    ChertError, NetworkError, APIError, ValidationError as ChertValidationError
)
from .types import (
    ClientConfig, NetworkStatus, Block, Transaction, APIResponse,
    JSONRPCRequest, JSONRPCResponse
)
from .wallet import WalletManager
from .privacy import PrivacyManager
from .staking import StakingManager
from .governance import GovernanceManager


class ChertClient:
    """
    Main client for interacting with the Chert blockchain.

    Example:
        >>> client = ChertClient()
        >>> account = await client.wallet.create_account()
        >>> print(f"Created account: {account.address}")
    """

    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize the Chert client.

        Args:
            config: Client configuration. If None, uses default configuration.
        """
        if config is None:
            config = ClientConfig()

        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None

        # Initialize managers
        self.wallet = WalletManager(self)
        self.privacy = PrivacyManager(self)
        self.staking = StakingManager(self)
        self.governance = GovernanceManager(self)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the client session."""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close the client session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def get_network_status(self) -> NetworkStatus:
        """
        Get current network status.

        Returns:
            Network status information.

        Raises:
            NetworkError: If the request fails.
            APIError: If the API returns an error.
        """
        return await self._rpc_call("getNetworkStatus", result_type=NetworkStatus)

    async def get_latest_block(self) -> Block:
        """
        Get the latest block information.

        Returns:
            Latest block data.

        Raises:
            NetworkError: If the request fails.
            APIError: If the API returns an error.
        """
        return await self._rpc_call("getLatestBlock", result_type=Block)

    async def get_block(self, height: int) -> Block:
        """
        Get block information by height.

        Args:
            height: Block height to retrieve.

        Returns:
            Block data for the specified height.

        Raises:
            NetworkError: If the request fails.
            APIError: If the API returns an error.
        """
        return await self._rpc_call("getBlock", [height], result_type=Block)

    async def get_transaction(self, tx_hash: str) -> Transaction:
        """
        Get transaction information by hash.

        Args:
            tx_hash: Transaction hash to retrieve.

        Returns:
            Transaction data.

        Raises:
            NetworkError: If the request fails.
            APIError: If the API returns an error.
        """
        return await self._rpc_call("getTransaction", [tx_hash], result_type=Transaction)

    async def is_connected(self) -> bool:
        """
        Check if the client is connected to the network.

        Returns:
            True if connected and responsive, False otherwise.
        """
        try:
            await self.get_network_status()
            return True
        except Exception:
            return False

    async def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Response data as dictionary.

        Raises:
            NetworkError: If the request fails.
            APIError: If the API returns an error.
        """
        if self._session is None:
            await self.start()

        url = urljoin(self.config.endpoint, path.lstrip('/'))

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Add API key if provided
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'

        # Add custom headers
        headers.update(self.config.headers)

        try:
            async with self._session.request(
                method,
                url,
                json=data,
                params=params,
                headers=headers
            ) as response:
                response_data = await response.json()

                if not response.ok:
                    error_msg = response_data.get('error', {}).get('message', 'Unknown API error')
                    error_code = response_data.get('error', {}).get('code', 'API_ERROR')
                    raise APIError(error_msg, error_code, response.status, response_data)

                api_response = APIResponse(**response_data)
                if not api_response.success:
                    if api_response.error:
                        raise APIError(
                            api_response.error.get('message', 'API request failed'),
                            api_response.error.get('code', 'API_ERROR'),
                            data=api_response.error
                        )
                    else:
                        raise APIError("API request failed", "API_ERROR")

                return api_response.data

        except aiohttp.ClientError as e:
            raise NetworkError(f"HTTP request failed: {e}") from e
        except ValidationError as e:
            raise ChertValidationError("response", f"Invalid response format: {e}") from e

    async def _rpc_call(
        self,
        method: str,
        params: Optional[Any] = None,
        result_type: Optional[type] = None
    ) -> Any:
        """
        Make a JSON-RPC call.

        Args:
            method: RPC method name
            params: RPC parameters
            result_type: Expected result type for validation

        Returns:
            RPC result data.

        Raises:
            NetworkError: If the request fails.
            APIError: If the RPC returns an error.
        """
        if self._session is None:
            await self.start()

        request = JSONRPCRequest(method=method, params=params)

        try:
            async with self._session.post(
                self.config.endpoint,
                json=request.dict(),
                headers={'Content-Type': 'application/json'}
            ) as response:
                response_data = await response.json()

                if not response.ok:
                    raise APIError(
                        f"HTTP {response.status}: RPC call failed",
                        "RPC_ERROR",
                        response.status
                    )

                rpc_response = JSONRPCResponse(**response_data)

                if rpc_response.error:
                    raise APIError(
                        rpc_response.error.get('message', 'RPC call failed'),
                        str(rpc_response.error.get('code', 'RPC_ERROR')),
                        data=rpc_response.error
                    )

                if result_type and rpc_response.result:
                    # Validate result type if specified
                    if hasattr(result_type, '__annotations__'):
                        return result_type(**rpc_response.result)
                    else:
                        return rpc_response.result

                return rpc_response.result

        except aiohttp.ClientError as e:
            raise NetworkError(f"RPC request failed: {e}") from e
        except ValidationError as e:
            raise ChertValidationError("rpc_response", f"Invalid RPC response format: {e}") from e


def generate_address(public_key: str) -> str:
    """
    Generate a deterministic address from a public key.

    Args:
        public_key: Hex-encoded public key.

    Returns:
        Blockchain address.
    """
    # Simple address generation for demonstration
    # In a real implementation, this would use proper cryptographic functions
    pub_key_bytes = bytes.fromhex(public_key)
    hash_obj = hashlib.sha256(pub_key_bytes)
    address = "chert_" + hash_obj.hexdigest()[:40]
    return address


def generate_tx_id() -> str:
    """
    Generate a new transaction ID.

    Returns:
        Unique transaction ID.
    """
    return secrets.token_hex(32)