"""
Contract configuration for different networks
"""

from dataclasses import dataclass
from eth_utils import to_checksum_address


@dataclass
class ProxyContractConfig:
    """Proxy Contract Configuration"""
    relay_hub: str
    proxy_factory: str


@dataclass
class SafeContractConfig:
    """Safe Contract Configuration"""
    safe_factory: str
    safe_multisend: str


@dataclass
class ContractConfig:
    """Contract Configuration"""
    proxy_contracts: ProxyContractConfig
    safe_contracts: SafeContractConfig


def is_proxy_contract_config_valid(config: ProxyContractConfig) -> bool:
    """Check if proxy contract config is valid"""
    return bool(config.relay_hub) and bool(config.proxy_factory)


def is_safe_contract_config_valid(config: SafeContractConfig) -> bool:
    """Check if safe contract config is valid"""
    return bool(config.safe_factory) and bool(config.safe_multisend)


# Polygon mainnet configuration
POL = ContractConfig(
    proxy_contracts=ProxyContractConfig(
        proxy_factory=to_checksum_address("0xaB45c5A4B0c941a2F231C04C3f49182e1A254052"),
        relay_hub=to_checksum_address("0xD216153c06E857cD7f72665E0aF1d7D82172F494")
    ),
    safe_contracts=SafeContractConfig(
        safe_factory=to_checksum_address("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"),
        safe_multisend=to_checksum_address("0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"),
    )
)

# Polygon Amoy testnet configuration
AMOY = ContractConfig(
    proxy_contracts=ProxyContractConfig(
        # Proxy factory unsupported on Amoy testnet
        relay_hub="",
        proxy_factory="",
    ),
    safe_contracts=SafeContractConfig(
        safe_factory=to_checksum_address("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"),
        safe_multisend=to_checksum_address("0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"),
    )
)


def get_contract_config(chain_id: int) -> ContractConfig:
    """Get contract configuration for chain ID"""
    if chain_id == 137:
        return POL
    elif chain_id == 80002:
        return AMOY
    else:
        raise ValueError("Invalid network")
