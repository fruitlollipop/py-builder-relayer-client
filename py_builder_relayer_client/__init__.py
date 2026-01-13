"""
Python client library for interacting with the Polymarket Relayer infrastructure
"""

from .client import RelayClient
from .signer import Signer
from .config import ContractConfig, SafeContractConfig, ProxyContractConfig, get_contract_config
from .config_manager import (
    RelayerClientConfig,
    create_client_from_config,
    create_client_from_env,
)
from .factory import (
    create_polygon_mainnet_client,
    create_polygon_testnet_client,
    create_read_only_client,
    create_client_with_builder_config,
)
from .models import (
    SafeTransaction,
    ProxyTransaction,
    Transaction,
    OperationType,
    CallType,
    RelayerTxType,
    TransactionType,
    SafeTransactionArgs,
    ProxyTransactionArgs,
    SafeCreateTransactionArgs,
    TransactionRequest,
    SignatureParams,
    RelayerTransactionState,
    SplitSig,
    AddressPayload,
    NoncePayload,
    RelayPayload,
    GetDeployedResponse,
    RelayerTransaction,
)
from .response import ClientRelayerTransactionResponse
from .exceptions import (
    RelayerClientException, 
    RelayerApiException,
    SignerUnavailableException,
    SafeDeployedException,
    SafeNotDeployedException,
    ConfigUnsupportedOnChainException,
    InvalidTransactionException,
    GasEstimationException,
)
from .builder.derive import derive, derive_safe, derive_proxy_wallet
from .transaction_builder import TransactionBuilder, get_contract_address
from .helpers import (
    create_erc20_approve_transaction,
    create_erc20_transfer_transaction,
    create_eth_transfer_transaction,
    create_contract_call_transaction,
    batch_transactions,
    estimate_gas_for_transactions,
)

__version__ = "0.0.1"

__all__ = [
    # Core client
    "RelayClient",
    "Signer",
    
    # Configuration
    "ContractConfig",
    "SafeContractConfig",
    "ProxyContractConfig",
    "get_contract_config",
    "RelayerClientConfig",
    "create_client_from_config",
    "create_client_from_env",
    
    # Factory functions
    "create_polygon_mainnet_client",
    "create_polygon_testnet_client",
    "create_read_only_client",
    "create_client_with_builder_config",
    
    # Models
    "SafeTransaction",
    "ProxyTransaction",
    "Transaction",
    "OperationType",
    "CallType",
    "RelayerTxType",
    "TransactionType",
    "SafeTransactionArgs",
    "ProxyTransactionArgs",
    "SafeCreateTransactionArgs",
    "TransactionRequest",
    "SignatureParams",
    "RelayerTransactionState",
    "SplitSig",
    "AddressPayload",
    "NoncePayload",
    "RelayPayload",
    "GetDeployedResponse",
    "RelayerTransaction",
    
    # Response handling
    "ClientRelayerTransactionResponse",
    
    # Exceptions
    "RelayerClientException",
    "RelayerApiException",
    "SignerUnavailableException",
    "SafeDeployedException", 
    "SafeNotDeployedException",
    "ConfigUnsupportedOnChainException",
    "InvalidTransactionException",
    "GasEstimationException",
    
    # Utilities
    "derive",
    "derive_safe",
    "derive_proxy_wallet",
    "TransactionBuilder",
    "get_contract_address",
    
    # Helper functions
    "create_erc20_approve_transaction",
    "create_erc20_transfer_transaction",
    "create_eth_transfer_transaction",
    "create_contract_call_transaction",
    "batch_transactions",
    "estimate_gas_for_transactions",
]