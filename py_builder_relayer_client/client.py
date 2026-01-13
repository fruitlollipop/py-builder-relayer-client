"""
Main RelayClient class for interacting with Polymarket relayer infrastructure
"""

import json
import time
from typing import List, Optional, Union, Any, Dict

from py_builder_signing_sdk.config import BuilderConfig
from py_builder_signing_sdk.models import BuilderHeaderPayload

from .models import (
    Transaction,
    SafeTransaction,
    ProxyTransaction,
    SafeTransactionArgs,
    ProxyTransactionArgs,
    SafeCreateTransactionArgs,
    RelayerTransaction,
    RelayerTransactionResponse,
    RelayerTxType,
    TransactionType,
    OperationType,
    CallType,
    NoncePayload,
    RelayPayload,
    GetDeployedResponse,
)
from .http_helpers import HttpClient, GET, POST, RequestOptions
from .endpoints import (
    GET_NONCE,
    GET_RELAY_PAYLOAD,
    GET_TRANSACTION,
    GET_TRANSACTIONS,
    SUBMIT_TRANSACTION,
    GET_DEPLOYED,
)
from .builder import (
    build_safe_transaction_request,
    build_safe_create_transaction_request,
    build_proxy_transaction_request,
    derive_safe,
)
from .encode import encode_proxy_transaction_data
from .config import (
    ContractConfig,
    get_contract_config,
    is_proxy_contract_config_valid,
    is_safe_contract_config_valid,
)
from .constants.constants import ZERO_ADDRESS
from .exceptions import (
    SIGNER_UNAVAILABLE,
    SAFE_DEPLOYED,
    SAFE_NOT_DEPLOYED,
    CONFIG_UNSUPPORTED_ON_CHAIN,
)
from .response import ClientRelayerTransactionResponse
from .utils import sleep_sync


class RelayClient:
    """
    Client for the Polymarket Relayer
    Supports both SAFE and PROXY transaction types
    """

    def __init__(
        self,
        relayer_url: str,
        chain_id: int,
        signer: Optional[Any] = None,
        builder_config: Optional[BuilderConfig] = None,
        relay_tx_type: Optional[RelayerTxType] = None,
    ):
        self.relayer_url = relayer_url[:-1] if relayer_url.endswith("/") else relayer_url
        self.chain_id = chain_id
        self.relay_tx_type = relay_tx_type if relay_tx_type is not None else RelayerTxType.SAFE
        self.contract_config = get_contract_config(chain_id)
        self.http_client = HttpClient()
        self.signer = signer
        self.builder_config = builder_config

    def get_nonce(self, signer_address: str, signer_type: str) -> NoncePayload:
        """Gets the nonce for the signer"""
        return self.send(
            GET_NONCE,
            GET,
            RequestOptions(params={"address": signer_address, "type": signer_type})
        )

    def get_relay_payload(self, signer_address: str, signer_type: str) -> RelayPayload:
        """Gets the relay payload for the signer"""
        return self.send(
            GET_RELAY_PAYLOAD,
            GET,
            RequestOptions(params={"address": signer_address, "type": signer_type})
        )

    def get_transaction(self, transaction_id: str) -> List[RelayerTransaction]:
        """Gets the transaction given the transaction_id"""
        return self.send(
            GET_TRANSACTION,
            GET,
            RequestOptions(params={"id": transaction_id})
        )

    def get_transactions(self) -> List[RelayerTransaction]:
        """Gets all transactions for the builder"""
        return self.send_authed_request(GET, GET_TRANSACTIONS)

    def execute(self, txns: List[Transaction], metadata: Optional[str] = None) -> RelayerTransactionResponse:
        """
        Executes a batch of transactions
        
        Args:
            txns: List of transactions to execute
            metadata: Optional metadata string
            
        Returns:
            RelayerTransactionResponse
        """
        self._signer_needed()
        
        if len(txns) == 0:
            raise Exception("no transactions to execute")

        if self.relay_tx_type == RelayerTxType.SAFE:
            return self._execute_safe_transactions(
                [SafeTransaction(
                    to=txn.to,
                    operation=OperationType.Call,
                    data=txn.data,
                    value="0"
                ) for txn in txns],
                metadata
            )
        elif self.relay_tx_type == RelayerTxType.PROXY:
            return self._execute_proxy_transactions(
                [ProxyTransaction(
                    to=txn.to,
                    type_code=CallType.Call,
                    data=txn.data,
                    value="0"
                ) for txn in txns],
                metadata
            )
        else:
            raise Exception(f"Unsupported relay transaction type: {self.relay_tx_type}")

    def _execute_safe_transactions(self, txns: List[SafeTransaction], metadata: Optional[str] = None) -> RelayerTransactionResponse:
        """Execute SAFE transactions"""
        self._signer_needed()
        print("Executing safe transactions...")
        
        safe = self._get_expected_safe()
        deployed = self.get_deployed(safe)
        if not deployed:
            raise SAFE_NOT_DEPLOYED
        
        start = time.time()
        from_address = self.signer.get_address()
        
        nonce_payload = self.get_nonce(from_address, TransactionType.SAFE.value)
        
        args = SafeTransactionArgs(
            transactions=txns,
            from_address=from_address,
            nonce=nonce_payload.nonce,
            chain_id=self.chain_id,
        )
        
        safe_contract_config = self.contract_config.safe_contracts
        if not is_safe_contract_config_valid(safe_contract_config):
            raise CONFIG_UNSUPPORTED_ON_CHAIN
        
        request = build_safe_transaction_request(
            self.signer,
            args,
            safe_contract_config,
            metadata,
        )
        
        print(f"Client side safe request creation took: {time.time() - start:.3f} seconds")
        
        request_payload = json.dumps(request.to_dict())
        
        resp = self.send_authed_request(POST, SUBMIT_TRANSACTION, request_payload)
        
        return ClientRelayerTransactionResponse(
            resp["transactionID"],
            resp["state"],
            resp["transactionHash"],
            self,
        )

    def _execute_proxy_transactions(self, txns: List[ProxyTransaction], metadata: Optional[str] = None) -> RelayerTransactionResponse:
        """Execute PROXY transactions"""
        self._signer_needed()
        print("Executing proxy transactions...")
        
        start = time.time()
        from_address = self.signer.get_address()
        
        rp = self.get_relay_payload(from_address, TransactionType.PROXY.value)
        
        args = ProxyTransactionArgs(
            from_address=from_address,
            gas_price="0",
            data=encode_proxy_transaction_data(txns),
            relay=rp.address,
            nonce=rp.nonce,
        )
        
        proxy_contract_config = self.contract_config.proxy_contracts
        if not is_proxy_contract_config_valid(proxy_contract_config):
            raise CONFIG_UNSUPPORTED_ON_CHAIN
        
        request = build_proxy_transaction_request(
            self.signer,
            args,
            proxy_contract_config,
            metadata,
        )
        
        print(f"Client side proxy request creation took: {time.time() - start:.3f} seconds")
        
        request_payload = json.dumps(request.to_dict())
        
        resp = self.send_authed_request(POST, SUBMIT_TRANSACTION, request_payload)
        
        return ClientRelayerTransactionResponse(
            resp["transactionID"],
            resp["state"],
            resp["transactionHash"],
            self,
        )

    def deploy(self) -> RelayerTransactionResponse:
        """
        Deploys a safe
        
        Returns:
            RelayerTransactionResponse
        """
        self._signer_needed()
        safe = self._get_expected_safe()
        
        deployed = self.get_deployed(safe)
        if deployed:
            raise SAFE_DEPLOYED
        
        print(f"Deploying safe {safe}...")
        return self._deploy()

    def _deploy(self) -> RelayerTransactionResponse:
        """Internal deploy method"""
        start = time.time()
        from_address = self.signer.get_address()
        
        args = SafeCreateTransactionArgs(
            from_address=from_address,
            chain_id=self.chain_id,
            payment_token=ZERO_ADDRESS,
            payment="0",
            payment_receiver=ZERO_ADDRESS,
        )
        
        safe_contract_config = self.contract_config.safe_contracts
        
        request = build_safe_create_transaction_request(
            self.signer,
            safe_contract_config,
            args
        )
        
        print(f"Client side deploy request creation took: {time.time() - start:.3f} seconds")
        
        request_payload = json.dumps(request.to_dict())
        
        resp = self.send_authed_request(POST, SUBMIT_TRANSACTION, request_payload)
        
        return ClientRelayerTransactionResponse(
            resp["transactionID"],
            resp["state"],
            resp["transactionHash"],
            self,
        )

    def get_deployed(self, safe: str) -> bool:
        """Returns a boolean that indicates if a safe is deployed"""
        resp: GetDeployedResponse = self.send(
            GET_DEPLOYED,
            GET,
            RequestOptions(params={"address": safe})
        )
        return resp.deployed

    def poll_until_state(
        self,
        transaction_id: str,
        states: List[str],
        fail_state: Optional[str] = None,
        max_polls: Optional[int] = None,
        poll_frequency: Optional[int] = None,
    ) -> Optional[RelayerTransaction]:
        """
        Periodically polls the transaction id until it reaches a desired state
        Returns the relayer transaction if it reaches the desired state
        Returns None if the transaction hits the failed state
        Times out after maxPolls is reached
        
        Args:
            transaction_id: Transaction ID to poll
            states: List of desired states
            fail_state: Optional fail state
            max_polls: Maximum number of polls (default: 10)
            poll_frequency: Poll frequency in milliseconds (default: 2000)
            
        Returns:
            RelayerTransaction or None
        """
        print(f"Waiting for transaction {transaction_id} matching states: {states}...")
        
        max_poll_count = max_polls if max_polls is not None else 10
        poll_freq = 2000  # Default to polling every 2 seconds
        if poll_frequency is not None and poll_frequency >= 1000:
            poll_freq = poll_frequency
        
        poll_count = 0
        while poll_count < max_poll_count:
            txns = self.get_transaction(transaction_id)
            if len(txns) > 0:
                txn = txns[0]
                if txn.state in states:
                    return txn
                if fail_state is not None and txn.state == fail_state:
                    print(f"txn {transaction_id} failed onchain! Transaction hash: {txn.transaction_hash}")
                    return None
            
            poll_count += 1
            time.sleep(poll_freq / 1000)
        
        print("Transaction not found or not in given states, timing out!")
        return None

    def send_authed_request(
        self,
        method: str,
        path: str,
        body: Optional[str] = None
    ) -> Any:
        """Send authenticated request with builder headers"""
        # Builder auth
        if self._can_builder_auth():
            builder_headers = self._generate_builder_headers(method, path, body)
            if builder_headers is not None:
                return self.send(
                    path,
                    method,
                    RequestOptions(headers=builder_headers, data=body)
                )
        
        return self.send(
            path,
            method,
            RequestOptions(data=body)
        )

    def _generate_builder_headers(
        self,
        method: str,
        path: str,
        body: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """Generate builder authentication headers"""
        if self.builder_config is not None:
            builder_headers = self.builder_config.generate_builder_headers(
                method,
                path,
                body,
            )
            if builder_headers is None:
                return None
            return builder_headers.to_dict()
        
        return None

    def _can_builder_auth(self) -> bool:
        """Check if builder authentication is available"""
        return self.builder_config is not None and self.builder_config.is_valid()

    def send(
        self,
        endpoint: str,
        method: str,
        options: Optional[RequestOptions] = None
    ) -> Any:
        """Send HTTP request"""
        resp = self.http_client.send(f"{self.relayer_url}{endpoint}", method, options)
        return resp.json()

    def _signer_needed(self) -> None:
        """Validate that signer is available"""
        if self.signer is None:
            raise SIGNER_UNAVAILABLE

    def _get_expected_safe(self) -> str:
        """Returns the expected safe for the signer"""
        address = self.signer.get_address()
        return derive_safe(address, self.contract_config.safe_contracts.safe_factory)
