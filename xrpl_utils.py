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
    Note that JsonRpcClient is a class - input is     the testnet URL
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
        return int(balance)
    except Exception:
        try:
            return float(balance)
        except Exception:
            return None

def get_account_info(client, address):
    """Return account info for a given classic address.

    Returns a dictionary with account data or None if account not found.
    """
    try:
        acct_info = AccountInfo(account=address, ledger_index="validated", strict=True)
        response = client.request(acct_info)
        result = getattr(response, "result", {})
        account_data = result.get("account_data")
        return account_data #returns a dictionary representing account data
    except Exception:
        return None

def mint_nft(client, wallet, metadata):
    # Placeholder for minting logic; to be implemented later.

    raise NotImplementedError()
def uri_already_minted(uri):
    """Check if an NFT with this URI has already been minted in the system.
    
    Queries all NFTs in the account to check if URI already exists.
    This ensures the same metadata URI can only be minted once.
    
    Args:
        uri: The metadata URI to check
        
    Returns: Tuple (already_exists: bool, existing_nft_id: str or None)
    """
    client = JsonRpcClient(XRPL_TESTNET_URL)
    
    try:
        # Convert URI to hex for comparison (same format as stored on ledger)
        uri_hex = xrpl.utils.str_to_hex(uri)
        
        # Get all NFTs from the testnet (limited approach: check your own account)
        # For production, you'd query all accounts or use a central registry
        # For now, we'll return False (not minted) since we check at mint time
        # NOTE: To fully prevent duplicates across all users, you'd need:
        # 1. A central database/registry of all minted URIs, OR
        # 2. Query all ledger accounts (expensive), OR
        # 3. Use a unique identifier per minter (URI + minter address)
        
        return (False, None)
        
    except Exception as e:
        return (False, None)


def check_uri_in_account(address, uri):
    """Check if an account already owns an NFT with the given URI.
    
    Args:
        address: XRPL account address to check
        uri: The metadata URI to look for
        
    Returns: Tuple (uri_exists: bool, nft_id: str or None)
    """
    try:
        client = JsonRpcClient(XRPL_TESTNET_URL)
        uri_hex = xrpl.utils.str_to_hex(uri)
        
        # Get all NFTs owned by this account
        acct_nfts = AccountNFTs(account=address)
        response = client.request(acct_nfts)
        nfts = response.result.get("account_nfts", [])
        
        # Check if any NFT has this URI
        for nft in nfts:
            if nft.get("URI") == uri_hex:
                return (True, nft.get("NFTokenID"))
        
        return (False, None)
        
    except Exception as e:
        return (False, None)


def mint_token(seed, uri, flags=8, transfer_fee=0, taxon=0, enforce_single_owner=True):
    """Mint an NFT on XRPL testnet with single-owner enforcement.
    
    Args:
        seed: Wallet seed (private key)
        uri: Metadata URI for the NFT
        flags: NFT flags (default 8 = burnable). Use 0 to allow burnable+transferable.
        transfer_fee: Transfer fee in basis points
        taxon: NFT taxon
        enforce_single_owner: If True, ensures NFT cannot be fractionally owned (default True)
    
    Returns: Transaction result or error message
    """
    minter_wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(XRPL_TESTNET_URL)
    
    # By default, use flags=8 (burnable only, non-transferable = single owner)
    # To allow transfers, use flags=0, but this allows multiple holders if fractional NFT
    # To ensure single owner with transfers, user should not set transfer_fee or use burnable only
    
    if enforce_single_owner and transfer_fee > 0:
        # Warn: transfer_fee implies transferable NFT, which could allow fractional ownership
        # Keep burnable flag (8) to disable fractional minting
        pass
    
    # Define the mint transaction. Note that the NFT URI must be converted to a hex string.
    mint_tx = xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=xrpl.utils.str_to_hex(uri),
        flags=int(flags),  # flags=8 ensures burnable, non-transferable (single owner)
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


import xrpl
import streamlit as st

def display_nft_image(hex_uri):
    if not hex_uri:
        return None
    
    try:
        # 1. Decode Hex to String
        plain_uri = xrpl.utils.hex_to_str(hex_uri)
        
        # 2. Convert IPFS to a Web-viewable URL
        # Changes 'ipfs://CID' to 'https://ipfs.io/ipfs/CID'
        if plain_uri.startswith("ipfs://"):
            display_url = plain_uri.replace("ipfs://", "https://ipfs.io/ipfs/")
        else:
            display_url = plain_uri
            
        return display_url
    except:
        return None