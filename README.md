# py-builder-relayer-client

Python client library for interacting with the Polymarket Relayer infrastructure

## Installation

```bash
pip install py-builder-relayer-client
```

## Quick Start

### Basic Usage

```python
from py_builder_relayer_client import create_polygon_testnet_client, TransactionBuilder, RelayerTxType

# Create a client for Polygon testnet with SAFE transaction type (default)
client = create_polygon_testnet_client(
    private_key="your_private_key",
    builder_api_key="your_api_key",
    builder_secret="your_secret",
    builder_passphrase="your_passphrase"
)

# Or create with PROXY transaction type
proxy_client = create_polygon_testnet_client(
    private_key="your_private_key",
    builder_api_key="your_api_key",
    builder_secret="your_secret",
    builder_passphrase="your_passphrase",
    relay_tx_type=RelayerTxType.PROXY
)

# Deploy your safe (SAFE type only - PROXY wallets auto-deploy)
if client.relay_tx_type == RelayerTxType.SAFE:
    safe_address = client.get_expected_safe()
    if not client.get_deployed(safe_address):
        deploy_response = client.deploy()
        deploy_response.wait()  # Wait for deployment

# Build and execute transactions
builder = TransactionBuilder()
builder.add_erc20_approve("0x...", "0x...", 1000000)  # Approve 1 USDC
builder.add_erc20_transfer("0x...", "0x...", 500000)  # Transfer 0.5 USDC

response = client.execute(builder.build(), "My transaction batch")
result = response.wait()  # Wait for completion
```

### Transaction Types

The client supports two transaction types via the `RelayerTxType` enum:

- **`RelayerTxType.SAFE`** (default): Executes transactions through Gnosis Safe contracts
- **`RelayerTxType.PROXY`**: Executes transactions through Polymarket Proxy wallets

```python
from py_builder_relayer_client import RelayClient, RelayerTxType

# SAFE transactions (default)
safe_client = RelayClient(
    relayer_url="https://relayer-v2-staging.polymarket.dev/",
    chain_id=80002,
    private_key="your_private_key",
    builder_config=builder_config,
    relay_tx_type=RelayerTxType.SAFE
)

# PROXY transactions
proxy_client = RelayClient(
    relayer_url="https://relayer-v2-staging.polymarket.dev/",
    chain_id=137,  # Proxy supported on mainnet
    private_key="your_private_key",
    builder_config=builder_config,
    relay_tx_type=RelayerTxType.PROXY
)
```

### Using Environment Variables

Create a `.env` file:

```env
RELAYER_URL=https://relayer-v2-staging.polymarket.dev/
CHAIN_ID=80002
PK=your_private_key_here
BUILDER_API_KEY=your_api_key
BUILDER_SECRET=your_api_secret
BUILDER_PASS_PHRASE=your_passphrase
```

Then use:

```python
from py_builder_relayer_client import create_client_from_env

client = create_client_from_env()
```

## Configuration

### Supported Networks

- **Polygon Mainnet** (Chain ID: 137)
- **Polygon Amoy Testnet** (Chain ID: 80002)

### Factory Functions

```python
from py_builder_relayer_client import (
    create_polygon_mainnet_client,
    create_polygon_testnet_client,
    create_read_only_client
)

# Mainnet client
mainnet_client = create_polygon_mainnet_client(
    private_key="...",
    builder_api_key="...",
    builder_secret="...",
    builder_passphrase="..."
)

# Testnet client
testnet_client = create_polygon_testnet_client(
    private_key="...",
    builder_api_key="...",
    builder_secret="...",
    builder_passphrase="..."
)

# Read-only client (no signing)
readonly_client = create_read_only_client(
    relayer_url="https://relayer-v2-staging.polymarket.dev/",
    chain_id=80002
)
```

## Transaction Building

### Using TransactionBuilder

```python
from py_builder_relayer_client import TransactionBuilder, get_contract_address

builder = TransactionBuilder()

# Get common contract addresses
usdc_address = get_contract_address(80002, "USDC")  # Testnet USDC

# Add various transaction types
builder.add_erc20_approve(usdc_address, spender_address, amount)
builder.add_erc20_transfer(usdc_address, recipient_address, amount)
builder.add_eth_transfer(recipient_address, amount_wei)
builder.add_contract_call(
    contract_address="0x...",
    function_signature="someFunction(uint256,address)",
    parameters=[123, "0x..."],
    parameter_types=["uint256", "address"]
)

# Build and execute
transactions = builder.build()
response = client.execute(transactions, "Batch transaction")
```

### Using Helper Functions

```python
from py_builder_relayer_client import (
    create_erc20_approve_transaction,
    create_erc20_transfer_transaction,
    create_eth_transfer_transaction
)

# Create individual transactions
approve_tx = create_erc20_approve_transaction(token_address, spender_address, amount)
transfer_tx = create_erc20_transfer_transaction(token_address, recipient_address, amount)
eth_tx = create_eth_transfer_transaction(recipient_address, amount_wei)

# Execute them
response = client.execute([approve_tx, transfer_tx, eth_tx], "Multiple transactions")
```

## Core Operations

### Safe Management

```python
# Get expected safe address
safe_address = client.get_expected_safe()

# Check if safe is deployed
is_deployed = client.get_deployed(safe_address)

# Deploy safe if needed
if not is_deployed:
    deploy_response = client.deploy()
    result = deploy_response.wait()
```

### Transaction Execution

```python
# Execute transactions
response = client.execute(transactions, metadata="Optional description")

# Wait for completion
result = response.wait()

# Check transaction status
if result:
    print(f"Success! Hash: {result.get('transactionHash')}")
    print(f"State: {result.get('state')}")
else:
    print("Transaction failed or timed out")
```

### Querying

```python
# Get nonce for an address
nonce_data = client.get_nonce(address, "SAFE")

# Get specific transaction
transaction = client.get_transaction(transaction_id)

# Get all transactions
all_transactions = client.get_transactions()

# Poll for transaction state
final_state = client.poll_until_state(
    transaction_id=tx_id,
    states=["STATE_MINED", "STATE_CONFIRMED"],
    fail_state="STATE_FAILED",
    max_polls=10,
    poll_frequency=3000  # 3 seconds
)
```

## Advanced Usage

### Custom Configuration

```python
from py_builder_relayer_client import RelayerClientConfig, create_client_from_config

config = RelayerClientConfig(
    relayer_url="https://custom-relayer.example.com/",
    chain_id=137,
    private_key="your_private_key",
    builder_api_key="your_api_key",
    builder_secret="your_secret",
    builder_passphrase="your_passphrase"
)

client = create_client_from_config(config)
```

### Error Handling

```python
from py_builder_relayer_client import RelayerClientException, RelayerApiException

try:
    response = client.execute(transactions)
    result = response.wait()
except RelayerApiException as e:
    print(f"API Error: {e.status_code} - {e.error_msg}")
except RelayerClientException as e:
    print(f"Client Error: {e.msg}")
```

### Transaction States

```python
from py_builder_relayer_client import RelayerTransactionState

# Available states
states = [
    RelayerTransactionState.STATE_NEW.value,
    RelayerTransactionState.STATE_EXECUTED.value,
    RelayerTransactionState.STATE_MINED.value,
    RelayerTransactionState.STATE_CONFIRMED.value,
    RelayerTransactionState.STATE_INVALID.value,
    RelayerTransactionState.STATE_FAILED.value,
]
```

## Examples

See the `examples/` directory for complete working examples:

- `deploy.py` - Basic safe deployment
- `execute.py` - Transaction execution
- `get_nonce.py` - Querying nonce
- `get_transaction.py` - Transaction retrieval
- `advanced_example.py` - Advanced features showcase
- `factory_example.py` - Using factory functions

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black py_builder_relayer_client/ tests/ examples/
```

## License

MIT License

