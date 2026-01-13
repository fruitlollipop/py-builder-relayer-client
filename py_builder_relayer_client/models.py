from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class RelayerTxType(Enum):
    SAFE = "SAFE"
    PROXY = "PROXY"


class TransactionType(Enum):
    SAFE = "SAFE"
    PROXY = "PROXY"
    SAFE_CREATE = "SAFE-CREATE"


class OperationType(Enum):
    Call = 0
    DelegateCall = 1


class CallType(Enum):
    Invalid = "0"
    Call = "1"
    DelegateCall = "2"


class RelayerTransactionState(Enum):
    STATE_NEW = "STATE_NEW"
    STATE_EXECUTED = "STATE_EXECUTED"
    STATE_MINED = "STATE_MINED"
    STATE_INVALID = "STATE_INVALID"
    STATE_CONFIRMED = "STATE_CONFIRMED"
    STATE_FAILED = "STATE_FAILED"


@dataclass
class SignatureParams:
    gas_price: Optional[str] = None
    
    # Proxy RelayHub sig params
    relayer_fee: Optional[str] = None
    gas_limit: Optional[str] = None
    relay_hub: Optional[str] = None
    relay: Optional[str] = None
    
    # SAFE sig parameters
    operation: Optional[str] = None
    safe_txn_gas: Optional[str] = None
    base_gas: Optional[str] = None
    gas_token: Optional[str] = None
    refund_receiver: Optional[str] = None
    
    # SAFE CREATE sig parameters
    payment_token: Optional[str] = None
    payment: Optional[str] = None
    payment_receiver: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        result = {}
        if self.gas_price is not None:
            result["gasPrice"] = self.gas_price
        if self.relayer_fee is not None:
            result["relayerFee"] = self.relayer_fee
        if self.gas_limit is not None:
            result["gasLimit"] = self.gas_limit
        if self.relay_hub is not None:
            result["relayHub"] = self.relay_hub
        if self.relay is not None:
            result["relay"] = self.relay
        if self.operation is not None:
            result["operation"] = self.operation
        if self.safe_txn_gas is not None:
            result["safeTxnGas"] = self.safe_txn_gas
        if self.base_gas is not None:
            result["baseGas"] = self.base_gas
        if self.gas_token is not None:
            result["gasToken"] = self.gas_token
        if self.refund_receiver is not None:
            result["refundReceiver"] = self.refund_receiver
        if self.payment_token is not None:
            result["paymentToken"] = self.payment_token
        if self.payment is not None:
            result["payment"] = self.payment
        if self.payment_receiver is not None:
            result["paymentReceiver"] = self.payment_receiver
        return result


@dataclass
class AddressPayload:
    address: str


@dataclass
class NoncePayload:
    nonce: str


@dataclass
class RelayPayload:
    address: str
    nonce: str


@dataclass
class TransactionRequest:
    type: str
    from_address: str
    to: str
    data: str
    signature: str
    signature_params: SignatureParams
    proxy_wallet: Optional[str] = None
    nonce: Optional[str] = None
    metadata: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "from": self.from_address,
            "to": self.to,
            "data": self.data,
            "signature": self.signature,
            "signatureParams": self.signature_params.to_dict(),
        }
        if self.proxy_wallet is not None:
            result["proxyWallet"] = self.proxy_wallet
        if self.nonce is not None:
            result["nonce"] = self.nonce
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result


@dataclass
class ProxyTransaction:
    to: str
    type_code: CallType
    data: str
    value: str


@dataclass
class SafeTransaction:
    to: str
    operation: OperationType
    data: str
    value: str


@dataclass
class Transaction:
    to: str
    data: str
    value: str


@dataclass
class SafeTransactionArgs:
    from_address: str
    nonce: str
    chain_id: int
    transactions: List[SafeTransaction]


@dataclass
class SafeCreateTransactionArgs:
    from_address: str
    chain_id: int
    payment_token: str
    payment: str
    payment_receiver: str


@dataclass
class ProxyTransactionArgs:
    from_address: str
    nonce: str
    gas_price: str
    data: str
    relay: str
    gas_limit: Optional[str] = None


@dataclass
class RelayerTransaction:
    transaction_id: str
    transaction_hash: str
    from_address: str
    to: str
    proxy_address: str
    data: str
    nonce: str
    value: str
    state: str
    type: str
    metadata: str
    created_at: datetime
    updated_at: datetime


@dataclass
class GetDeployedResponse:
    deployed: bool


@dataclass
class SplitSig:
    r: str
    s: str
    v: str
