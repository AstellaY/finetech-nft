import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.requests import AccountNFTs

testnet_url = "https://s.altnet.rippletest.net:51234"

def mint_token(seed, uri, flags=8, transfer_fee=0, taxon=0):
#Get the account wallet and a client instance.
    """mint_token"""
    minter_wallet=Wallet.from_seed(seed)
    client=JsonRpcClient(testnet_url)
#Define the mint transaction. Note that the NFT URI must be converted to a hex string.
    mint_tx=xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=xrpl.utils.str_to_hex(uri),
        flags=int(flags),
        transfer_fee=int(transfer_fee),
        nftoken_taxon=int(taxon)
    )
#Submit the transaction and return results.
    reply=""
    try:
        response=xrpl.transaction.submit_and_wait(mint_tx,client,minter_wallet)
        reply=response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply=f"Submit failed: {e}"
    return reply


def get_tokens(account):
    """get_tokens"""
#Instantiate a client.
    client=JsonRpcClient(testnet_url)
#Prepare the AccountNFTs request.
    acct_nfts=AccountNFTs(
        account=account
    )
#Submit the request and return results.
    response=client.request(acct_nfts)
    return response.result

#Pass the owner's seed value and the NFT ID.
def burn_token(seed, nftoken_id):
    """burn_token"""
#Get the owner wallet and client instance.
    owner_wallet=Wallet.from_seed(seed)
    client=JsonRpcClient(testnet_url)
#Define the NFTokenBurn transaction.
    burn_tx=xrpl.models.transactions.NFTokenBurn(
        account=owner_wallet.address,
        nftoken_id=nftoken_id    
    )
#Submit the transaction and return results.
    reply=""
    try:
        response=xrpl.transaction.submit_and_wait(burn_tx,client,owner_wallet)
        reply=response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply=f"Submit failed: {e}"
    return reply