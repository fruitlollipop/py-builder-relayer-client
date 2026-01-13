"""
Utility functions
"""

import asyncio
import time
from dataclasses import dataclass
from eth_abi.packed import encode_packed
from hexbytes import HexBytes


@dataclass
class SplitSig:
    r: str
    s: str
    v: str


def split_and_pack_sig(sig: str) -> str:
    """
    Split signature and pack it into Gnosis accepted rsv format
    
    Args:
        sig: Signature as hex string
        
    Returns:
        Packed signature as hex string
    """
    split_sig = split_signature(sig)
    
    # Pack the signature
    packed_sig = encode_packed(
        ["uint256", "uint256", "uint8"],
        [int(split_sig.r), int(split_sig.s), int(split_sig.v)]
    )
    
    return "0x" + packed_sig.hex()


def split_signature(sig: str) -> SplitSig:
    """
    Split signature into r, s, v components
    
    Args:
        sig: Signature as hex string
        
    Returns:
        SplitSig object with r, s, v components
    """
    # Remove 0x prefix if present
    if sig.startswith('0x'):
        sig = sig[2:]
    
    # Extract v from the last byte
    sig_v = int(sig[-2:], 16)
    
    # Adjust v value according to Gnosis Safe requirements
    if sig_v in (0, 1):
        sig_v += 31
    elif sig_v in (27, 28):
        sig_v += 4
    else:
        raise ValueError("Invalid signature")
    
    # Update the signature with the new v value
    sig = sig[:-2] + f"{sig_v:02x}"
    
    # Extract r, s, v
    r = int(sig[0:64], 16)
    s = int(sig[64:128], 16)
    v = int(sig[128:130], 16)
    
    return SplitSig(
        r=str(r),
        s=str(s),
        v=str(v)
    )


def sleep_sync(ms: int) -> None:
    """
    Sleep for the specified number of milliseconds (synchronous)
    
    Args:
        ms: Number of milliseconds to sleep
    """
    time.sleep(ms / 1000.0)


async def sleep(seconds: float) -> None:
    """
    Async sleep function
    
    Args:
        seconds: Number of seconds to sleep
    """
    await asyncio.sleep(seconds)