from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.requests.account_info import AccountInfo


def connect_xrpl():
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
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


def mint_nft(client, wallet, metadata):
    # Placeholder for minting logic; to be implemented later.
    raise NotImplementedError()
