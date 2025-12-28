# Chert SDK for Python

[![PyPI version](https://badge.fury.io/py/chert-sdk.svg)](https://pypi.org/project/chert-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/chert-sdk.svg)](https://pypi.org/project/chert-sdk/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for the Chert/Silica blockchain network.

## Features

- **Async/Await Support**: Modern Python async programming
- **Type Hints**: Full type annotations for better IDE support
- **Pydantic Models**: Data validation and serialization
- **Wallet Management**: Create and manage accounts, send transactions
- **Privacy Features**: Stealth addresses and private transactions
- **Staking**: Delegate tokens to validators and manage stakes
- **Governance**: Participate in network governance and voting
- **Network Operations**: Query blockchain state and network information

## Installation

```bash
pip install chert-sdk
```

Or from source:

```bash
git clone https://github.com/silica-network/chert.git
cd chert/sdk/python
pip install -e .
```

## Quick Start

```python
import asyncio
from chert_sdk import ChertClient

async def main():
    # Create a client
    client = ChertClient()

    # Create a new account
    account = await client.wallet.create_account()
    print(f"Created account: {account.address}")

    # Get network status
    status = await client.get_network_status()
    print(f"Block height: {status.block_height}")

    # Send a transaction
    tx_request = {
        "to": "recipient_address",
        "amount": "100.0",
        "fee": "0.1",
        "memo": "Hello Chert!"
    }

    tx_hash = await client.wallet.send_transaction(tx_request, account)
    print(f"Transaction sent: {tx_hash}")

asyncio.run(main())
```

## Usage Examples

### Wallet Operations

```python
from chert_sdk import ChertClient

async def wallet_example():
    client = ChertClient()

    # Create account
    account = await client.wallet.create_account()
    print(f"Address: {account.address}")
    print(f"Public Key: {account.public_key}")

    # Import account from private key
    imported = await client.wallet.import_account("your_private_key_hex")
    print(f"Imported: {imported.address}")

    # Get balance
    balance = await client.wallet.get_balance(account.address)
    print(f"Balance: {balance.available} available")

    # Send transaction
    tx_hash = await client.wallet.send_transaction({
        "to": imported.address,
        "amount": "50.0",
        "fee": "0.05",
        "memo": "Test transaction"
    }, account)

    # Wait for confirmation
    confirmed_tx = await client.wallet.wait_for_transaction(tx_hash)
    if confirmed_tx:
        print(f"Transaction confirmed: {confirmed_tx.status}")
```

### Privacy Features

```python
from chert_sdk import ChertClient, PrivacyLevel

async def privacy_example():
    client = ChertClient()

    # Generate stealth keys
    stealth_keys = await client.privacy.generate_stealth_keys()
    print(f"View key: {stealth_keys.view_keypair.public}")

    # Create stealth account
    stealth_account = await client.privacy.create_stealth_account(
        stealth_keys.view_keypair.secret,
        stealth_keys.spend_keypair.public,
        stealth_keys
    )
    print(f"Stealth address: {stealth_account.address}")

    # Send private transaction
    private_tx = await client.privacy.send_private_transaction({
        "sender_keys": stealth_keys,
        "recipient_view_key": "recipient_view_key",
        "amount": "25.0",
        "fee": "0.02",
        "privacy_level": PrivacyLevel.STEALTH,
        "memo": "Private message",
        "nonce": 1
    }, "recipient_view_key", "recipient_spend_key")

    print(f"Private transaction: {private_tx}")
```

### Staking Operations

```python
from chert_sdk import ChertClient

async def staking_example():
    client = ChertClient()

    # Get validators
    validators = await client.staking.get_validators()
    for validator in validators[:3]:  # Show first 3
        print(f"Validator: {validator.name} ({validator.status})")

    # Delegate tokens
    account = await client.wallet.create_account()
    delegation_tx = await client.staking.delegate(
        account.address,
        validators[0].address,
        "1000.0",
        "0.1"
    )
    print(f"Delegation transaction: {delegation_tx}")

    # Get staking rewards
    rewards = await client.staking.get_staking_rewards(account.address)
    print(f"Available rewards: {rewards.available}")
```

### Governance Operations

```python
from chert_sdk import ChertClient, VoteOption

async def governance_example():
    client = ChertClient()

    # Get proposals
    proposals = await client.governance.get_proposals(limit=5)
    for proposal in proposals:
        print(f"Proposal: {proposal.title} ({proposal.status})")

    # Create a proposal
    account = await client.wallet.create_account()
    proposal_id = await client.governance.create_proposal(
        "Network Upgrade",
        "Proposal to upgrade the network to version 2.0",
        account.address,
        "1.0"
    )
    print(f"Created proposal: {proposal_id}")

    # Vote on proposal
    vote_tx = await client.governance.vote(
        proposal_id,
        account.address,
        VoteOption.YES,
        "0.1"
    )
    print(f"Vote cast: {vote_tx}")
```

## Configuration

```python
from chert_sdk import ChertClient, ClientConfig, Network

# Custom configuration
config = ClientConfig(
    endpoint="https://api.chert.com",
    network=Network.TESTNET,
    timeout=45.0,  # 45 seconds
    api_key="your_api_key",
    headers={
        "X-Custom-Header": "value"
    }
)

client = ChertClient(config)
```

## Async Context Manager

```python
from chert_sdk import ChertClient

async def example():
    async with ChertClient() as client:
        # Client automatically handles session lifecycle
        account = await client.wallet.create_account()
        print(f"Account: {account.address}")
```

## Error Handling

```python
from chert_sdk import ChertClient
from chert_sdk.exceptions import APIError, NetworkError, ValidationError

async def error_handling_example():
    client = ChertClient()

    try:
        balance = await client.wallet.get_balance("invalid_address")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except NetworkError as e:
        print(f"Network error: {e}")
    except APIError as e:
        print(f"API error {e.code}: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Testing

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=chert_sdk --cov-report=html
```

## API Reference

For complete API documentation, see the [API Reference](api_reference.md).

## Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

This SDK handles cryptographic operations and private keys. Always:

- Use strong, randomly generated private keys
- Never log or expose private keys
- Use HTTPS endpoints in production
- Keep dependencies updated
- Audit your code for security vulnerabilities