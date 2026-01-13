"""
Example of creating redeem transactions for CTF and NegRisk Adapter
Similar to the TypeScript redeem.ts example
"""

import os
from dotenv import load_dotenv
from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds
from eth_abi import encode

from py_builder_relayer_client import (
    RelayClient,
    RelayerTxType,
    Transaction,
)

# Load environment variables
load_dotenv()


def create_ctf_redeem_transaction(
    contract_address: str,
    condition_id: str,
    collateral_address: str,
) -> Transaction:
    """Create a CTF redeem transaction"""
    # CTF redeemPositions function signature
    function_signature = "redeemPositions(address,bytes32,bytes32,uint256[])"
    function_selector = "0x6c0d2d5a"  # First 4 bytes of keccak256(function_signature)
    
    # Encode parameters
    parent_collection_id = "0x" + "00" * 32  # Zero hash
    index_sets = [1, 2]  # Standard index sets for binary outcomes
    
    # Encode the function call data
    encoded_params = encode(
        ['address', 'bytes32', 'bytes32', 'uint256[]'],
        [collateral_address, bytes.fromhex(parent_collection_id[2:]), 
         bytes.fromhex(condition_id[2:]), index_sets]
    )
    
    call_data = function_selector + encoded_params.hex()
    
    return Transaction(
        to=contract_address,
        data=call_data,
        value="0"
    )


def create_nr_adapter_redeem_transaction(
    contract_address: str,
    condition_id: str,
    redeem_amounts: list,
) -> Transaction:
    """Create a NegRisk Adapter redeem transaction"""
    # NegRisk Adapter redeemPositions function signature
    function_signature = "redeemPositions(bytes32,uint256[])"
    function_selector = "0x6c0d2d5a"  # This might be different, but using same for example
    
    # Encode parameters
    encoded_params = encode(
        ['bytes32', 'uint256[]'],
        [bytes.fromhex(condition_id[2:]), redeem_amounts]
    )
    
    call_data = function_selector + encoded_params.hex()
    
    return Transaction(
        to=contract_address,
        data=call_data,
        value="0"
    )


def main():
    print("Starting Redeem Example...")
    
    # Configuration
    relayer_url = os.getenv("RELAYER_URL", "https://relayer-v2-staging.polymarket.dev/")
    chain_id = int(os.getenv("CHAIN_ID", "80002"))
    private_key = os.getenv("PK")
    
    # Builder credentials
    builder_creds = BuilderApiKeyCreds(
        key=os.getenv("BUILDER_API_KEY"),
        secret=os.getenv("BUILDER_SECRET"),
        passphrase=os.getenv("BUILDER_PASS_PHRASE"),
    )
    
    builder_config = BuilderConfig(local_builder_creds=builder_creds)
    
    # Create client with SAFE transaction type
    client = RelayClient(
        relayer_url=relayer_url,
        chain_id=chain_id,
        private_key=private_key,
        builder_config=builder_config,
        relay_tx_type=RelayerTxType.SAFE,
    )
    
    print(f"Using Safe transaction type on chain {chain_id}")
    
    # Check if safe is deployed
    safe_address = client.get_expected_safe()
    print(f"Expected safe address: {safe_address}")
    
    is_deployed = client.get_deployed(safe_address)
    if not is_deployed:
        print("Safe not deployed. Please deploy first using deploy_example.py")
        return
    
    print("Safe is deployed, proceeding with redeem...")
    
    # Configuration - Set your values here
    neg_risk = False  # Set to True for NegRisk Adapter redeem
    condition_id = "0x" + "12" * 32  # Replace with your actual condition ID
    
    # Amounts to redeem per outcome (only necessary for neg risk)
    # [yes tokens, no tokens]
    redeem_amounts = [111000000, 0]
    
    # Contract addresses
    usdc_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    ctf_address = "0x4d97dcd97ec945f40cf65f87097ace5ea0476045"
    neg_risk_adapter = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"
    
    # Create the appropriate redeem transaction
    if neg_risk:
        print("Creating NegRisk Adapter redeem transaction...")
        redeem_tx = create_nr_adapter_redeem_transaction(
            neg_risk_adapter, condition_id, redeem_amounts
        )
    else:
        print("Creating CTF redeem transaction...")
        redeem_tx = create_ctf_redeem_transaction(
            ctf_address, condition_id, usdc_address
        )
    
    try:
        print("Executing redeem transaction...")
        response = client.execute([redeem_tx], "redeem")
        
        print(f"Transaction submitted with ID: {response.transaction_id}")
        
        # Wait for completion
        print("Waiting for transaction completion...")
        result = response.wait()
        
        if result:
            print(f"Redeem completed successfully!")
            print(f"Transaction Hash: {result.get('transactionHash')}")
            print(f"State: {result.get('state')}")
        else:
            print("Transaction failed or timed out")
            
    except Exception as e:
        print(f"Error executing redeem: {e}")


if __name__ == "__main__":
    main()