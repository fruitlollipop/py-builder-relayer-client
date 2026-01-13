"""
SAFE creation transaction building
"""

from eth_account.messages import encode_structured_data
from ..models import (
    SafeCreateTransactionArgs,
    SignatureParams,
    TransactionType,
    TransactionRequest,
)
from ..constants.constants import SAFE_FACTORY_NAME
from .derive import derive_safe
from ..config import SafeContractConfig


def create_safe_create_signature(
    signer,
    safe_factory: str,
    chain_id: int,
    payment_token: str,
    payment: str,
    payment_receiver: str,
) -> str:
    """Create signature for SAFE creation using EIP-712"""
    domain = {
        "name": SAFE_FACTORY_NAME,
        "chainId": chain_id,
        "verifyingContract": safe_factory,
    }
    
    types = {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "CreateProxy": [
            {"name": "paymentToken", "type": "address"},
            {"name": "payment", "type": "uint256"},
            {"name": "paymentReceiver", "type": "address"},
        ],
    }
    
    values = {
        "paymentToken": payment_token,
        "payment": int(payment),
        "paymentReceiver": payment_receiver,
    }
    
    # Create EIP-712 structured data
    structured_data = {
        "types": types,
        "primaryType": "CreateProxy",
        "domain": domain,
        "message": values,
    }
    
    sig = signer.sign_typed_data(domain, types, values, "CreateProxy")
    print(f"Sig: {sig}")
    return sig


def build_safe_create_transaction_request(
    signer,
    safe_contract_config: SafeContractConfig,
    args: SafeCreateTransactionArgs,
) -> TransactionRequest:
    """Build a SAFE creation transaction request"""
    safe_factory = safe_contract_config.safe_factory
    
    sig = create_safe_create_signature(
        signer,
        safe_factory,
        args.chain_id,
        args.payment_token,
        args.payment,
        args.payment_receiver
    )
    
    sig_params = SignatureParams(
        payment_token=args.payment_token,
        payment=args.payment,
        payment_receiver=args.payment_receiver,
    )
    
    safe_address = derive_safe(args.from_address, safe_factory)
    
    request = TransactionRequest(
        from_address=args.from_address,
        to=safe_factory,
        # Note: obviously the safe here does not exist yet but useful to have this data in the db
        proxy_wallet=safe_address,
        data="0x",
        signature=sig,
        signature_params=sig_params,
        type=TransactionType.SAFE_CREATE,
    )
    
    print("Created a SAFE-CREATE Transaction:")
    print(request.to_dict())
    return request
