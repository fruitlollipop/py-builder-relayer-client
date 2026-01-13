"""
PROXY transaction building
"""

from typing import Optional
from Crypto.Hash import keccak
from ..models import (
    ProxyTransactionArgs,
    TransactionRequest,
    SignatureParams,
    TransactionType,
)
from ..config import ProxyContractConfig
from .derive import derive_proxy_wallet

DEFAULT_GAS_LIMIT = 10_000_000


def create_struct_hash(
    from_address: str,
    to: str,
    data: str,
    tx_fee: str,
    gas_price: str,
    gas_limit: str,
    nonce: str,
    relay_hub_address: str,
    relay_address: str,
) -> str:
    """Create struct hash for proxy transaction signing"""
    # RelayHub prefix
    relay_hub_prefix = b"rlx:"
    
    # Convert addresses to bytes (20 bytes each)
    encoded_from = bytes.fromhex(from_address[2:] if from_address.startswith('0x') else from_address)
    encoded_to = bytes.fromhex(to[2:] if to.startswith('0x') else to)
    encoded_data = bytes.fromhex(data[2:] if data.startswith('0x') else data)
    encoded_tx_fee = int(tx_fee).to_bytes(32, 'big')
    encoded_gas_price = int(gas_price).to_bytes(32, 'big')
    encoded_gas_limit = int(gas_limit).to_bytes(32, 'big')
    encoded_nonce = int(nonce).to_bytes(32, 'big')
    encoded_relay_hub = bytes.fromhex(relay_hub_address[2:] if relay_hub_address.startswith('0x') else relay_hub_address)
    encoded_relay = bytes.fromhex(relay_address[2:] if relay_address.startswith('0x') else relay_address)
    
    # Concatenate all data
    data_to_hash = (
        relay_hub_prefix +
        encoded_from +
        encoded_to +
        encoded_data +
        encoded_tx_fee +
        encoded_gas_price +
        encoded_gas_limit +
        encoded_nonce +
        encoded_relay_hub +
        encoded_relay
    )
    
    # Hash using keccak256
    hash_obj = keccak.new(digest_bits=256)
    hash_obj.update(data_to_hash)
    return '0x' + hash_obj.hexdigest()


def create_proxy_signature(signer, struct_hash: str) -> str:
    """Sign a proxy transaction struct hash"""
    return signer.sign_message(struct_hash)


def get_gas_limit(signer, to: str, args: ProxyTransactionArgs) -> str:
    """Get gas limit for proxy transaction"""
    if hasattr(args, 'gas_limit') and args.gas_limit and args.gas_limit != "0":
        return args.gas_limit
    
    try:
        # Estimate gas
        gas_limit_big_int = signer.estimate_gas({
            "from": args.from_address,
            "to": to,
            "data": args.data,
        })
        return str(gas_limit_big_int)
    except Exception as e:
        print(f"Error estimating gas for proxy transaction, using default gas limit: {e}")
        return str(DEFAULT_GAS_LIMIT)


def build_proxy_transaction_request(
    signer,
    args: ProxyTransactionArgs,
    proxy_contract_config: ProxyContractConfig,
    metadata: Optional[str] = None,
) -> TransactionRequest:
    """Build a proxy transaction request"""
    proxy_wallet_factory = proxy_contract_config.proxy_factory
    to = proxy_wallet_factory
    proxy = derive_proxy_wallet(args.from_address, proxy_wallet_factory)
    relayer_fee = "0"
    relay_hub = proxy_contract_config.relay_hub
    gas_limit_str = get_gas_limit(signer, to, args)
    
    sig_params = SignatureParams(
        gas_price=args.gas_price,
        gas_limit=gas_limit_str,
        relayer_fee=relayer_fee,
        relay_hub=relay_hub,
        relay=args.relay,
    )
    
    tx_hash = create_struct_hash(
        args.from_address,
        to,
        args.data,
        relayer_fee,
        args.gas_price,
        gas_limit_str,
        args.nonce,
        relay_hub,
        args.relay
    )
    
    sig = create_proxy_signature(signer, tx_hash)
    
    if metadata is None:
        metadata = ""
    
    req = TransactionRequest(
        from_address=args.from_address,
        to=to,
        proxy_wallet=proxy,
        data=args.data,
        nonce=args.nonce,
        signature=sig,
        signature_params=sig_params,
        type=TransactionType.PROXY,
        metadata=metadata,
    )
    
    print("Created Proxy Transaction Request:")
    print(req.to_dict())
    return req