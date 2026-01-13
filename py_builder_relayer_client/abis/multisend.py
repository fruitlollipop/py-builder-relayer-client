"""
Multisend ABI
"""

MULTISEND_ABI = [
    {
        "constant": False,
        "inputs": [
            {
                "internalType": "bytes",
                "name": "transactions",
                "type": "bytes"
            }
        ],
        "name": "multiSend",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]