"""finetech NFT — Streamlit UI frontend for XRPL testnet interactions."""

import streamlit as st
import xrpl_utils
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    MSG_CONNECTED,
    MSG_WALLET_ADDRESS,
    MSG_WALLET_SEED,
    MSG_WALLET_BALANCE,
    MSG_NO_ACCOUNT,
    MSG_MINTING_FUTURE,
)


@st.cache_resource
def get_xrpl_client():
    """Get cached XRPL client to avoid redundant connections."""
    return xrpl_utils.connect_xrpl()


def main():
    """Main Streamlit app."""
    # Header
    st.title(APP_TITLE)
    st.write(f"Welcome to {APP_SUBTITLE}")

    # Connect to XRPL (cached)
    client = get_xrpl_client()
    st.success(MSG_CONNECTED)

    # Section 1: Generate Wallet
    st.header("Create / Inspect Testnet Wallet")
    if st.button("Generate Testnet Wallet"):
        wallet = xrpl_utils.generate_test_wallet(client)
        st.write(MSG_WALLET_ADDRESS, wallet.classic_address)
        st.write(MSG_WALLET_SEED, wallet.seed)
        bal = xrpl_utils.get_account_balance(client, wallet.classic_address)
        st.write(MSG_WALLET_BALANCE, bal)

    st.markdown("---")

    # Section 2: Check Balance
    st.header("Check Balance for an Existing Address")
    addr = st.text_input("Enter a classic address (r...) to check balance")
    if addr:
        bal = xrpl_utils.get_account_balance(client, addr)
        if bal is None:
            st.error(MSG_NO_ACCOUNT)
        else:
            st.write("Balance (XRP):", bal)

    st.markdown("\n\n")
    st.info(MSG_MINTING_FUTURE)


if __name__ == "__main__":
    main()

