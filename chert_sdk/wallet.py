"""
Wallet manager for account operations and transaction management.
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional

from .client import ChertClient, generate_address
from .exceptions import WalletError, TransactionError, ValidationError
from .types import Account, Balance, TransactionRequest, Transaction, TransactionStatus


class WalletManager:
    """Handles wallet operations and account management."""

    def __init__(self, client: ChertClient):
        self.client = client

    async def create_account(self) -> Account:
        """
        Create a new account with a randomly generated keypair.

        Returns:
            New account with generated keys.

        Raises:
            WalletError: If key generation fails.
        """
        try:
            private_key, public_key = self._generate_keypair()
            address = generate_address(public_key)

            return Account(
                address=address,
                public_key=public_key,
                private_key=private_key
            )
        except Exception as e:
            raise WalletError(f"Failed to create account: {e}") from e

    async def import_account(self, private_key: str) -> Account:
        """
        Import an account from a private key.

        Args:
            private_key: Hex-encoded private key.

        Returns:
            Account derived from the private key.

        Raises:
            ValidationError: If the private key is invalid.
            WalletError: If key derivation fails.
        """
        try:
            # Validate private key format
            if not private_key or len(private_key) != 64:
                raise ValidationError("private_key", "Private key must be 64 hex characters")

            bytes.fromhex(private_key)  # Validate hex format

            public_key = self._derive_public_key(private_key)
            address = generate_address(public_key)

            return Account(
                address=address,
                public_key=public_key,
                private_key=private_key
            )
        except ValueError as e:
            raise ValidationError("private_key", "Invalid hex format") from e
        except Exception as e:
            raise WalletError(f"Failed to import account: {e}") from e

    async def create_watch_only_account(self, public_key: str) -> Account:
        """
        Create a watch-only account from a public key.

        Args:
            public_key: Hex-encoded public key.

        Returns:
            Watch-only account.

        Raises:
            ValidationError: If the public key is invalid.
        """
        try:
            # Validate public key format
            if not public_key or len(public_key) != 64:
                raise ValidationError("public_key", "Public key must be 64 hex characters")

            bytes.fromhex(public_key)  # Validate hex format

            address = generate_address(public_key)

            return Account(
                address=address,
                public_key=public_key
            )
        except ValueError as e:
            raise ValidationError("public_key", "Invalid hex format") from e

    async def get_balance(self, address: str) -> Balance:
        """
        Get the balance for an account.

        Args:
            address: Account address.

        Returns:
            Account balance information.

        Raises:
            ValidationError: If the address is invalid.
            NetworkError: If the request fails.
        """
        if not address:
            raise ValidationError("address", "Address cannot be empty")

        return await self.client._rpc_call("getBalance", [address], Balance)

    async def send_transaction(self, request: TransactionRequest, account: Account) -> str:
        """
        Send a transaction to the network.

        Args:
            request: Transaction request details.
            account: Account to send from.

        Returns:
            Transaction hash.

        Raises:
            ValidationError: If the request or account is invalid.
            TransactionError: If the transaction fails.
            WalletError: If signing fails.
        """
        if not account.private_key:
            raise WalletError("Account does not have a private key")

        # Validate request
        self._validate_transaction_request(request)

        # Sign transaction
        signature = self._sign_transaction(request, account.private_key)

        # Prepare transaction data
        tx_data = {
            "sender": account.address,
            "recipient": request.to,
            "amount": request.amount,
            "fee": request.fee,
            "nonce": request.nonce or 0,
            "signature": signature,
        }

        if request.memo:
            tx_data["memo"] = request.memo

        # Send transaction
        result = await self.client._rpc_call("sendTransaction", [tx_data])

        if isinstance(result, dict) and "hash" in result:
            return result["hash"]

        raise TransactionError("Invalid transaction response")

    async def estimate_fee(self, request: TransactionRequest) -> dict:
        """
        Estimate the fee for a transaction.

        Args:
            request: Transaction request details.

        Returns:
            Fee estimation data.

        Raises:
            ValidationError: If the request is invalid.
        """
        self._validate_transaction_request(request)
        return await self.client._rpc_call("estimateFee", [request.dict()])

    async def wait_for_transaction(
        self,
        tx_hash: str,
        timeout_ms: int = 60000,
        interval_ms: int = 2000
    ) -> Optional[Transaction]:
        """
        Wait for a transaction to be confirmed.

        Args:
            tx_hash: Transaction hash to wait for.
            timeout_ms: Maximum time to wait in milliseconds.
            interval_ms: Polling interval in milliseconds.

        Returns:
            Transaction data if confirmed, None if timeout.

        Raises:
            ValidationError: If the transaction hash is invalid.
        """
        if not tx_hash:
            raise ValidationError("tx_hash", "Transaction hash cannot be empty")

        start_time = asyncio.get_event_loop().time() * 1000
        interval_seconds = interval_ms / 1000.0

        while (asyncio.get_event_loop().time() * 1000) - start_time < timeout_ms:
            try:
                tx = await self.client.get_transaction(tx_hash)

                if tx.status in [TransactionStatus.CONFIRMED]:
                    return tx
                elif tx.status in [TransactionStatus.FAILED, TransactionStatus.REJECTED]:
                    raise TransactionError(f"Transaction {tx.status}")

                await asyncio.sleep(interval_seconds)

            except Exception:
                # Continue polling if transaction not found yet
                await asyncio.sleep(interval_seconds)

        return None

    def _generate_keypair(self) -> tuple[str, str]:
        """Generate a new Ed25519 keypair."""
        # Generate 32 bytes of random data for private key
        private_key_bytes = secrets.token_bytes(32)
        private_key = private_key_bytes.hex()

        # For demonstration, derive public key from private key
        # In a real implementation, this would use proper Ed25519 derivation
        public_key_bytes = hashlib.sha256(private_key_bytes).digest()
        public_key = public_key_bytes.hex()

        return private_key, public_key

    def _derive_public_key(self, private_key: str) -> str:
        """Derive public key from private key."""
        private_key_bytes = bytes.fromhex(private_key)

        # For demonstration, hash the private key
        # In a real implementation, this would use proper Ed25519 derivation
        public_key_bytes = hashlib.sha256(private_key_bytes).digest()
        return public_key_bytes.hex()

    def _validate_transaction_request(self, request: TransactionRequest) -> None:
        """Validate a transaction request."""
        if not request.to:
            raise ValidationError("to", "Recipient address cannot be empty")

        if not request.amount:
            raise ValidationError("amount", "Amount cannot be empty")

        if not request.fee:
            raise ValidationError("fee", "Fee cannot be empty")

        # Basic amount validation
        try:
            float(request.amount)
        except ValueError:
            raise ValidationError("amount", "Invalid amount format")

        try:
            float(request.fee)
        except ValueError:
            raise ValidationError("fee", "Invalid fee format")

    def _sign_transaction(self, request: TransactionRequest, private_key: str) -> str:
        """Sign a transaction with the private key."""
        # Create transaction hash for signing
        tx_data = f"{request.to}{request.amount}{request.fee}{request.nonce or 0}"
        if request.memo:
            tx_data += request.memo

        # Simple signature for demonstration
        # In a real implementation, this would use proper Ed25519 signing
        signature_data = tx_data + private_key
        signature_hash = hashlib.sha256(signature_data.encode()).digest()
        signature = signature_hash.hex()

        return signature