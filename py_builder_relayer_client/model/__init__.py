"""
EIP712 model definitions
"""

from .base import BaseEIP712Model
from .safe_tx import SafeTx
from .create_proxy import CreateProxy

__all__ = [
    "BaseEIP712Model",
    "SafeTx",
    "CreateProxy",
]