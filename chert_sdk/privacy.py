"""
Privacy manager for stealth addresses and private transactions.
"""

import hashlib
import secrets
from typing import Optional

from .client import ChertClient
from .exceptions import PrivacyError, ValidationError
from .types import (
    StealthKeys, KeyPair, StealthAccount, PrivacyLevel,
    PrivateTransactionRequest, PrivateTransaction
)


class PrivacyManager:
    """Handles privacy features like stealth addresses."""

    def __init__(self, client: ChertClient):
        self.client = client

    async def generate_stealth_keys(self) -> StealthKeys:
        """
        Generate a new set of stealth keys.

        Returns:
            New stealth keys.

        Raises:
            PrivacyError: If key generation fails.
        """
        try:
            view_private, view_public = self._generate_keypair()
            spend_private, spend_public = self._generate_keypair()

            return StealthKeys(
                view_keypair=KeyPair(public=view_public, secret=view_private),
                spend_keypair=KeyPair(public=spend_public, secret=spend_private)
            )
        except Exception as e:
            raise PrivacyError(f"Failed to generate stealth keys: {e}") from e

    async def create_stealth_account(
        self,
        view_key: str,
        spend_public_key: str,
        keys: Optional[StealthKeys] = None
    ) -> StealthAccount:
        """
        Create a stealth account from keys.

        Args:
            view_key: View key for the account.
            spend_public_key: Spend public key.
            keys: Optional complete key set.

        Returns:
            Stealth account.

        Raises:
            ValidationError: If keys are invalid.
        """
        if not view_key or not spend_public_key:
            raise ValidationError("keys", "View key and spend public key are required")

        # Generate deterministic address
        address_data = view_key + spend_public_key
        address_hash = hashlib.sha256(address_data.encode()).hexdigest()
        address = f"stealth_{address_hash[:40]}"

        return StealthAccount(
            address=address,
            view_key=view_key,
            spend_public_key=spend_public_key,
            keys=keys
        )

    async def derive_shared_secret(self, view_key: str, recipient_view_key: str) -> str:
        """
        Derive a shared secret for encryption.

        Args:
            view_key: Sender's view key.
            recipient_view_key: Recipient's view key.

        Returns:
            Shared secret for encryption.
        """
        combined = view_key + recipient_view_key
        secret_hash = hashlib.sha256(combined.encode()).digest()
        return secret_hash.hex()

    async def encrypt_memo(self, memo: str, shared_secret: str) -> str:
        """
        Encrypt a memo using a shared secret.

        Args:
            memo: Memo to encrypt.
            shared_secret: Shared secret for encryption.

        Returns:
            Encrypted memo.
        """
        secret_bytes = bytes.fromhex(shared_secret)
        memo_bytes = memo.encode()

        # Simple XOR encryption for demonstration
        encrypted = bytearray()
        for i, b in enumerate(memo_bytes):
            encrypted.append(b ^ secret_bytes[i % len(secret_bytes)])

        return encrypted.hex()

    async def decrypt_memo(self, encrypted_memo: str, shared_secret: str) -> str:
        """
        Decrypt a memo using a shared secret.

        Args:
            encrypted_memo: Encrypted memo to decrypt.
            shared_secret: Shared secret for decryption.

        Returns:
            Decrypted memo.
        """
        secret_bytes = bytes.fromhex(shared_secret)
        encrypted_bytes = bytes.fromhex(encrypted_memo)

        # XOR decryption
        decrypted = bytearray()
        for i, b in enumerate(encrypted_bytes):
            decrypted.append(b ^ secret_bytes[i % len(secret_bytes)])

        return decrypted.decode()

    async def send_private_transaction(
        self,
        request: PrivateTransactionRequest,
        recipient_view_key: str,
        recipient_spend_key: str
    ) -> str:
        """
        Send a private transaction.

        Args:
            request: Private transaction request.
            recipient_view_key: Recipient's view key.
            recipient_spend_key: Recipient's spend key.

        Returns:
            Transaction ID.

        Raises:
            PrivacyError: If the transaction fails.
        """
        try:
            # Generate ephemeral keys
            ephemeral_keys = await self.generate_stealth_keys()

            # Derive shared secret
            shared_secret = await self.derive_shared_secret(
                request.sender_keys.view_keypair.secret,
                recipient_view_key
            )

            # Encrypt memo if provided
            encrypted_memo = None
            if request.memo:
                encrypted_memo = await self.encrypt_memo(request.memo, shared_secret)

            tx_data = {
                "sender_keys": request.sender_keys.dict(),
                "recipient_view_key": recipient_view_key,
                "recipient_spend_key": recipient_spend_key,
                "ephemeral_keys": ephemeral_keys.dict(),
                "amount": request.amount,
                "fee": request.fee,
                "privacy_level": request.privacy_level.value,
                "nonce": request.nonce,
            }

            if encrypted_memo:
                tx_data["encrypted_memo"] = encrypted_memo

            result = await self.client._rpc_call("sendPrivateTransaction", [tx_data])

            if isinstance(result, dict) and "tx_id" in result:
                return result["tx_id"]

            raise PrivacyError("Invalid private transaction response")

        except Exception as e:
            raise PrivacyError(f"Failed to send private transaction: {e}") from e

    def _generate_keypair(self) -> tuple[str, str]:
        """Generate a random keypair."""
        private_key_bytes = secrets.token_bytes(32)
        private_key = private_key_bytes.hex()

        # Derive public key (simplified for demo)
        public_key_bytes = hashlib.sha256(private_key_bytes).digest()
        public_key = public_key_bytes.hex()

        return private_key, public_key