"""XRPL blockchain utilities and wallet operations."""
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.models.requests.account_info import AccountInfo
from xrpl.models.requests import AccountNFTs
from config import XRPL_TESTNET_URL
import requests
import json
import binascii

# Pinata JWT - Ensure this is the long token, not the API Key
PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI1MGM0OGM4Zi0yMzI5LTQyYmQtOWMzMC05NDIyYWMzZWRiOWIiLCJlbWFpbCI6ImFzdGVsbGF5aXBAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjUyYTU0NzYxMjM4MDdhOTAyOGVmIiwic2NvcGVkS2V5U2VjcmV0IjoiYzljYzcxYzQzOTE1MzE4OTc2MjkwYzA4ZDdlNTEyODBhNWJkOWE1OTkzNjFmYThjYzVjNTIzMzRkZDM1YTE0MSIsImV4cCI6MTc5OTQyMjQzOX0.-HHqKG6mofbs8-JJupUnPjmj3mXVMow7mYverg5dmMc"


def upload_to_ipfs(file_bytes, file_name):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    # Cleaning the JWT to prevent 'segment' errors
    clean_jwt = PINATA_JWT.strip()
    if len(clean_jwt.split('.')) != 3:
        raise Exception("JWT Format Error: Ensure you copied the full Pinata JWT.")

    headers = {"Authorization": f"Bearer {clean_jwt}"}
    files = {"file": (file_name, file_bytes)}
    
    try:
        # Added timeout to prevent the app from hanging on large files
        response = requests.post(url, headers=headers, files=files, timeout=30)
        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            raise Exception(f"Pinata {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Pinata Connection Failed: {e}")

def display_nft_image(hex_uri):
    if not hex_uri: return None
    try:
        # 1. Decode Hex to String
        plain_str = binascii.unhexlify(hex_uri).decode('utf-8')
        # 2. Parse JSON
        data = json.loads(plain_str)
        # 3. Handle shorthand 'i' or old 'im'
        img_url = data.get("i") or data.get("im")
        
        if img_url and img_url.startswith("ipfs://"):
            return img_url.replace("ipfs://", "https://gateway.pinata.cloud/ipfs/")
        return img_url
    except:
        return None


def connect_xrpl():
    return JsonRpcClient(XRPL_TESTNET_URL)

def generate_test_wallet(client):
    return generate_faucet_wallet(client, debug=True)

def get_account_info(client, address):
    try:
        acct_info = AccountInfo(account=address, ledger_index="validated", strict=True)
        response = client.request(acct_info)
        return response.result.get("account_data")
    except Exception: return None

def mint_token(seed, uri_hex, flags=8, transfer_fee=0, taxon=0):
    minter_wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(XRPL_TESTNET_URL)
    
    mint_tx = xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=uri_hex, 
        flags=int(flags),
        transfer_fee=int(transfer_fee),
        nftoken_taxon=int(taxon)
    )
    
    # submit_and_wait ensures the transaction is validated before moving to the next loop item
    response = xrpl.transaction.submit_and_wait(mint_tx, client, minter_wallet)
    return response.result

def get_tokens(account):
    client = JsonRpcClient(XRPL_TESTNET_URL)
    acct_nfts = AccountNFTs(account=account)
    response = client.request(acct_nfts)
    return response.result

def display_nft_image(hex_uri):
    if not hex_uri: return None
    try:
        plain_str = binascii.unhexlify(hex_uri).decode('utf-8')
        data = json.loads(plain_str)
        img_url = data.get("i") or data.get("im")
        
        if img_url and img_url.startswith("ipfs://"):
            return img_url.replace("ipfs://", "https://gateway.pinata.cloud/ipfs/")
        return img_url
    except: return None