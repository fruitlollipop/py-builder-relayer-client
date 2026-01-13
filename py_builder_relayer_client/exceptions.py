"""
Error definitions for the builder relayer client
"""

SIGNER_UNAVAILABLE = Exception("signer is needed to interact with this endpoint!")

SAFE_DEPLOYED = Exception("safe already deployed!")

SAFE_NOT_DEPLOYED = Exception("safe not deployed!")

CONFIG_UNSUPPORTED_ON_CHAIN = Exception("config is not supported on the chainId")
