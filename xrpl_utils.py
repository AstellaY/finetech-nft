"""XRPL blockchain utilities and wallet operations."""

import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.wallet import Wallet
from xrpl.models.requests.account_info import AccountInfo
from xrpl.models.requests import AccountNFTs
from config import XRPL_TESTNET_URL
from xrpl.models.transactions import NFTokenMint, NFTokenBurn

def connect_xrpl():
    """Connect to XRPL testnet (Altnet).

    Returns a JsonRpcClient instance.
    """
    client = JsonRpcClient(XRPL_TESTNET_URL)
    return client


def generate_test_wallet(client):
    """Create a funded testnet wallet via the XRPL faucet.

    Returns an xrpl.wallet.Wallet object with attributes like
    `classic_address` and `seed`.
    """
    wallet = generate_faucet_wallet(client, debug=True)
    return wallet


def get_account_balance(client, address):
    """Return account balance in XRP for a given classic address.

    Returns a float (XRP) or None if account not found.
    """
    acct_info = AccountInfo(account=address, ledger_index="validated", strict=True)
    response = client.request(acct_info)
    result = getattr(response, "result", {})
    balance = result.get("account_data", {}).get("Balance")
    if balance is None:
        return None
    try:
        return int(balance) / 1_000_000
    except Exception:
        try:
            return float(balance)
        except Exception:
            return None










def mint_token(seed, uri, flags=8, transfer_fee=0, taxon=0):
    """Mint an NFT on XRPL testnet.
    
    Args:
        seed: Wallet seed (private key)
        uri: Metadata URI for the NFT
        flags: NFT flags (default 8 = burnable)
        transfer_fee: Transfer fee in basis points
        taxon: NFT taxon
    
    Returns: Transaction result or error message
    """
    minter_wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(XRPL_TESTNET_URL)
    
    # Define the mint transaction. Note that the NFT URI must be converted to a hex string.
    mint_tx = xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=xrpl.utils.str_to_hex(uri),
        flags=int(flags),
        transfer_fee=int(transfer_fee),
        nftoken_taxon=int(taxon)
    )
    
    # Submit the transaction and return results.
    reply = ""
    try:
        response = xrpl.transaction.submit_and_wait(mint_tx, client, minter_wallet)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply = f"Submit failed: {e}"
    return reply





def get_tokens(account):
    """Retrieve NFTs owned by an account.
    
    Args:
        account: XRPL account address
        
    Returns: List of NFTs
    """
    client = JsonRpcClient(XRPL_TESTNET_URL)
    
    # Prepare the AccountNFTs request.
    acct_nfts = AccountNFTs(account=account)
    
    # Submit the request and return results.
    response = client.request(acct_nfts)
    return response.result

#Pass the owner's seed value and the NFT ID.
def burn_token(seed, nftoken_id):
    """Burn (delete) an NFT from the ledger.
    
    Args:
        seed: Wallet seed (private key)
        nftoken_id: ID of the NFT to burn
        
    Returns: Transaction result or error message
    """
    owner_wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(XRPL_TESTNET_URL)
    
    # Define the NFTokenBurn transaction.
    burn_tx = xrpl.models.transactions.NFTokenBurn(
        account=owner_wallet.address,
        nftoken_id=nftoken_id    
    )
    
    # Submit the transaction and return results.
    reply = ""
    try:
        response = xrpl.transaction.submit_and_wait(burn_tx, client, owner_wallet)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply = f"Submit failed: {e}"
    return reply


 
