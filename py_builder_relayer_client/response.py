"""
Response handling and polling
"""

from typing import List, Optional
from .models import RelayerTransaction, RelayerTransactionResponse, RelayerTransactionState


class ClientRelayerTransactionResponse(RelayerTransactionResponse):
    """Response wrapper that provides convenient methods for transaction polling"""
    
    def __init__(self, transaction_id: str, state: str, transaction_hash: str, client):
        self.client = client
        self.transaction_id = transaction_id
        self.transaction_hash = transaction_hash
        self.hash = transaction_hash  # Alias for compatibility
        self.state = state

    def get_transaction(self) -> List[RelayerTransaction]:
        """Get transaction details"""
        return self.client.get_transaction(self.transaction_id)

    def wait(self) -> Optional[RelayerTransaction]:
        """
        Poll until STATE_MINED or STATE_CONFIRMED
        Returns None on STATE_FAILED
        Max 100 polls with 2-second intervals
        """
        return self.client.poll_until_state(
            self.transaction_id,
            [
                RelayerTransactionState.STATE_MINED.value,
                RelayerTransactionState.STATE_CONFIRMED.value,
            ],
            RelayerTransactionState.STATE_FAILED.value,
            100,  # max polls
        )
