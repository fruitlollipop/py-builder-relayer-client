"""
Proxy transaction encoding utilities
"""

from typing import List
from eth_abi import encode
from ..models import ProxyTransaction, CallType


def encode_proxy_transaction_data(transactions: List[ProxyTransaction]) -> str:
    """
    Encode proxy transaction data for batch execution using the proxy ABI
    
    Args:
        transactions: List of proxy transactions to encode
        
    Returns:
        Encoded transaction data as hex string
    """
    if not transactions:
        return "0x"
    
    # Convert ProxyTransaction objects to the format expected by the proxy ABI
    calls = []
    for tx in transactions:
        call_tuple = (
            int(tx.type_code.value),  # typeCode as uint8
            tx.to,                    # to as address
            int(tx.value),           # value as uint256
            bytes.fromhex(tx.data[2:] if tx.data.startswith('0x') else tx.data)  # data as bytes
        )
        calls.append(call_tuple)
    
    # Encode using the proxy function signature
    # function proxy((uint8,address,uint256,bytes)[]) returns (bytes[])
    function_selector = "0x4b64e492"  # proxy function selector
    
    try:
        # Encode the calls array as tuple[]
        encoded_params = encode(
            ['(uint8,address,uint256,bytes)[]'],
            [calls]
        )
        
        return function_selector + encoded_params.hex()
        
    except Exception as e:
        # Fallback to simple concatenation if encoding fails
        print(f"Warning: Failed to encode proxy transactions properly: {e}")
        return "0x" + "".join(tx.data[2:] if tx.data.startswith('0x') else tx.data for tx in transactions)


def validate_proxy_transaction(transaction: ProxyTransaction) -> bool:
    """
    Validate a proxy transaction
    
    Args:
        transaction: The proxy transaction to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not transaction.to:
        return False
    
    if transaction.type_code not in [CallType.Call, CallType.DelegateCall]:
        return False
    
    if not transaction.data:
        return False
    
    try:
        int(transaction.value)
    except (ValueError, TypeError):
        return False
    
    return True