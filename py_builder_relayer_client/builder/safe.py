"""
SAFE transaction building
"""

from typing import List, Optional
from eth_account.messages import encode_structured_data
from hexbytes import HexBytes

from ..config import SafeContractConfig
from ..models import (
    SafeTransaction,
    OperationType,
    TransactionRequest,
    SafeTransactionArgs,
    SignatureParams,
    TransactionType,
)
from ..encode.safe import create_safe_multisend_transaction
from .derive import derive_safe
from ..constants.constants import ZERO_ADDRESS
from ..utils import split_and_pack_sig


def create_safe_signature(signer, struct_hash: str) -> str:
    """Signs a struct hash to generate a safe signature"""
    return signer.sign_message(struct_hash)


def create_struct_hash(
    chain_id: int,
    safe: str,
    to: str,
    value: str,
    data: str,
    operation: OperationType,
    safe_tx_gas: str,
    base_gas: str,
    gas_price: str,
    gas_token: str,
    refund_receiver: str,
    nonce: str,
) -> str:
    """Creates a Safe struct hash using EIP-712"""
    domain = {
        "chainId": chain_id,
        "verifyingContract": safe,
    }

    types = {
        "EIP712Domain": [
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "SafeTx": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "data", "type": "bytes"},
            {"name": "operation", "type": "uint8"},
            {"name": "safeTxGas", "type": "uint256"},
            {"name": "baseGas", "type": "uint256"},
            {"name": "gasPrice", "type": "uint256"},
            {"name": "gasToken", "type": "address"},
            {"name": "refundReceiver", "type": "address"},
            {"name": "nonce", "type": "uint256"},
        ],
    }

    values = {
        "to": to,
        "value": int(value),
        "data": HexBytes(data),
        "operation": operation.value,
        "safeTxGas": int(safe_tx_gas),
        "baseGas": int(base_gas),
        "gasPrice": int(gas_price),
        "gasToken": gas_token,
        "refundReceiver": refund_receiver,
        "nonce": int(nonce),
    }

    # Create EIP-712 structured data
    structured_data = {
        "types": types,
        "primaryType": "SafeTx",
        "domain": domain,
        "message": values,
    }

    # Hash the structured data
    encoded = encode_structured_data(structured_data)
    return encoded.hex()


def aggregate_transaction(txns: List[SafeTransaction], safe_multisend: str) -> SafeTransaction:
    """Aggregate multiple transactions into a single transaction"""
    if len(txns) == 1:
        return txns[0]
    else:
        return create_safe_multisend_transaction(txns, safe_multisend)


def build_safe_transaction_request(
    signer,
    args: SafeTransactionArgs,
    safe_contract_config: SafeContractConfig,
    metadata: Optional[str] = None,
) -> TransactionRequest:
    """
    Generate a Safe Transaction Request for the Relayer API
    """
    safe_factory = safe_contract_config.safe_factory
    safe_multisend = safe_contract_config.safe_multisend
    transaction = aggregate_transaction(args.transactions, safe_multisend)
    safe_txn_gas = "0"
    base_gas = "0"
    gas_price = "0"
    gas_token = ZERO_ADDRESS
    refund_receiver = ZERO_ADDRESS

    safe_address = derive_safe(args.from_address, safe_factory)

    # Generate the struct hash
    struct_hash = create_struct_hash(
        args.chain_id,
        safe_address,
        transaction.to,
        transaction.value,
        transaction.data,
        transaction.operation,
        safe_txn_gas,
        base_gas,
        gas_price,
        gas_token,
        refund_receiver,
        args.nonce,
    )

    sig = create_safe_signature(signer, struct_hash)

    # Split the sig then pack it into Gnosis accepted rsv format
    packed_sig = split_and_pack_sig(sig)

    sig_params = SignatureParams(
        gas_price=gas_price,
        operation=str(transaction.operation.value),
        safe_txn_gas=safe_txn_gas,
        base_gas=base_gas,
        gas_token=gas_token,
        refund_receiver=refund_receiver,
    )

    if metadata is None:
        metadata = ""

    req = TransactionRequest(
        from_address=args.from_address,
        to=transaction.to,
        proxy_wallet=safe_address,
        data=transaction.data,
        nonce=args.nonce,
        signature=packed_sig,
        signature_params=sig_params,
        type=TransactionType.SAFE,
        metadata=metadata,
    )

    print("Created Safe Transaction Request:")
    print(req.to_dict())
    return req
