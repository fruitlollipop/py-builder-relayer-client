from eth_abi import encode
from eth_abi.packed import encode_packed
from eth_utils import to_bytes, to_checksum_address, keccak

from ..constants.constants import SAFE_INIT_CODE_HASH, PROXY_INIT_CODE_HASH


def get_create2_address(bytecode_hash: str, from_address: str, salt: bytes) -> str:
    """
    Calculate CREATE2 address
    
    Args:
        bytecode_hash: The keccak256 hash of the init code
        from_address: The factory contract address
        salt: The salt bytes
        
    Returns:
        The calculated CREATE2 address
    """
    # Remove 0x prefix if present
    if bytecode_hash.startswith("0x"):
        bytecode_hash = bytecode_hash[2:]
    if from_address.startswith("0x"):
        from_address = from_address[2:]

    # Convert to bytes
    bytecode_hash_bytes = to_bytes(hexstr=bytecode_hash)
    from_address_bytes = to_bytes(hexstr=from_address)

    prefix = b"\xff"

    # CREATE2: keccak256(0xff + from + salt + keccak256(initCode))
    address_hash = keccak(prefix + from_address_bytes + salt + bytecode_hash_bytes)
    address = address_hash[-20:].hex()

    return to_checksum_address(address)


def derive_safe(address: str, safe_factory: str) -> str:
    """
    Derive Safe address using CREATE2
    Uses ABI encoding for salt generation (matches TypeScript deriveSafe)
    
    Args:
        address: The owner address
        safe_factory: The Safe factory contract address
        
    Returns:
        The derived Safe address
    """
    address = to_checksum_address(address)
    safe_factory = to_checksum_address(safe_factory)

    # Use ABI encoding for Safe (matches TypeScript encodeAbiParameters)
    salt = keccak(encode(["address"], [address]))
    safe_address = get_create2_address(
        bytecode_hash=SAFE_INIT_CODE_HASH, 
        from_address=safe_factory, 
        salt=salt
    )
    return to_checksum_address(safe_address)


def derive_proxy_wallet(address: str, proxy_factory: str) -> str:
    """
    Derive Proxy wallet address using CREATE2
    Uses packed encoding for salt generation (matches TypeScript deriveProxyWallet)
    
    Args:
        address: The owner address
        proxy_factory: The Proxy factory contract address
        
    Returns:
        The derived Proxy wallet address
    """
    address = to_checksum_address(address)
    proxy_factory = to_checksum_address(proxy_factory)

    # Use packed encoding for Proxy (matches TypeScript encodePacked)
    salt = keccak(encode_packed(["address"], [address]))
    proxy_address = get_create2_address(
        bytecode_hash=PROXY_INIT_CODE_HASH,
        from_address=proxy_factory,
        salt=salt
    )
    return to_checksum_address(proxy_address)


# Backward compatibility aliases
def derive(address: str, safe_factory: str) -> str:
    """
    DEPRECATED: Use derive_safe instead
    Kept for backward compatibility
    """
    return derive_safe(address, safe_factory)
